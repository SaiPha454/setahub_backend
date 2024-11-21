from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException, UploadFile, File
from fastapi.requests import Request
from typing import Dict, List
from services.message_service import create_message_service, get_messages_service, get_unread_messages_service, create_message_image_service
from sqlalchemy.orm import Session
from database_connection import get_db
from datetime import datetime, timezone
from schemas.message_schema import MessageSent
from fastapi.responses import JSONResponse

from models.booking_model import get_booking_between_two_users

router = APIRouter(
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)


class ConnectionManager:
    def __init__(self):
        self.connection_pools : Dict[int, WebSocket] = {}
        self.active_users : Dict[int] = {}
        self.chatting_users : Dict[int, Dict[str, int]] = {} #{ 1 : { "user_id":1, "peer_user_id": 2 }  }
    
    async def connect(self, socket: WebSocket, user_id: int):
        await socket.accept()
        self.connection_pools[user_id] = socket
        self.active_users[user_id] = True

        await self.broadcast({
            "type":"users_status",
            "active_users":self.active_users,
            "detail":{
                "join": True,
                "user_id": user_id
            }
        })

        
    async def disconnect(self, user_id: int):
        
        if user_id in self.connection_pools:
            del self.connection_pools[user_id]
            del self.active_users[user_id]

        await self.broadcast({
            "type":"users_status",
            "active_users":self.active_users,
            "detail":{
                "join": False,
                "user_id": user_id
            }
        })

    async def send_to_personal(self,to_user_id : int, data: dict):
        
        if to_user_id in self.connection_pools:
            
            socket = self.connection_pools[to_user_id]
            await socket.send_json(data)


    async def broadcast(self, data: dict):
        for key in self.connection_pools:
            await self.connection_pools[key].send_json(data)

    async def send_typing_signal(self, to_user_id: int, data: dict):
       
        if to_user_id in self.active_users:
            socket = self.connection_pools[to_user_id]
            await socket.send_json(data)

    async def add_chatting_user(self, from_user_id: int, to_user_id: int):
        self.chatting_users[from_user_id] = {"user_id": from_user_id, "peer_user_id": to_user_id}

    async def remove_chatting_user(self, user_id: int):
        if user_id in self.chatting_users:
            del self.chatting_users[user_id]

    async def is_peer_chatting(self, from_user_id: int, to_user_id: int):

        if to_user_id in self.chatting_users and self.chatting_users[to_user_id]["peer_user_id"] == from_user_id:
            return True
        return False





connection_manager = ConnectionManager()

@router.websocket("/chatting/{from_id}")
async def chatting_connection_handler(websocket: WebSocket, from_id: int):
    

    await connection_manager.connect(websocket, from_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            print("Receive Data : ", data)

            if data["type"] == "typing":
                to_user_id =int ( data["data"]["to_user_id"])
                await connection_manager.send_typing_signal(to_user_id=to_user_id, data=data)

            if data["type"] == "chatting":
                from_user_id = int( data["data"]["from_user_id"])
                to_user_id = int( data["data"]["to_user_id"] )
                if from_user_id in connection_manager.connection_pools:
                    
                    if data["chatting"] == True: # case of user get in the conversation box ( reading messages)
                        await connection_manager.add_chatting_user(from_user_id=from_user_id, to_user_id=to_user_id)
                    else:
                        await connection_manager.remove_chatting_user(user_id=from_id)
            print(connection_manager.chatting_users)
    except WebSocketDisconnect:
        await connection_manager.disconnect(from_id)


@router.post("/messages/{from_user_id}/to/{to_user_id}")
async def send_message(from_user_id: int, to_user_id: int, data: MessageSent , db: Session = Depends(get_db)):

    # Check if two uers are allowed to message each other
    booking = await get_booking_between_two_users(db=db, user1_id=from_user_id, user2_id=to_user_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Cannot send message to this user without schedule"
            }
        )
    if booking.status == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Cannot send message. Booking expires"
            }
        )
    if int(from_user_id) not in connection_manager.connection_pools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status":"fail",
                "message":"No Websocket connection"
            }
        )
    
    msg_status = "sent"
    if await connection_manager.is_peer_chatting(from_user_id=from_user_id, to_user_id=to_user_id):
        
        msg_status = "read"

    created_message = await create_message_service(
                    db=db, 
                    from_user_id=data.data.from_user_id, 
                    to_user_id=data.data.to_user_id,
                    message=data.data.message, 
                    msg_type=data.data.msg_type,
                    status= msg_status
                )
    

    message_data = {
        "type":"message",
        "data": created_message
    }

    await connection_manager.send_to_personal(to_user_id=message_data["data"]["to_user_id"], data=message_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"fail",
            "data": message_data
        }
    )



@router.post("/messages/{from_user_id}/to/{to_user_id}/images")
async def send_message(request: Request, from_user_id: int, to_user_id: int, image: UploadFile = File(...) , db: Session = Depends(get_db)):

    if image.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Only image files are allowed (jpeg, png, gif)."
            }
        )
    
    # Check if two uers are allowed to message each other
    booking = await get_booking_between_two_users(db=db, user1_id=from_user_id, user2_id=to_user_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Cannot send message to this user without schedule"
            }
        )
    
    if int(from_user_id) not in connection_manager.connection_pools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status":"fail",
                "message":"No Websocket connection"
            }
        )
    
    msg_status = "sent"
    if await connection_manager.is_peer_chatting(from_user_id=from_user_id, to_user_id=to_user_id):
        
        msg_status = "read"

    created_message = await create_message_image_service(
                    request= request, 
                    db=db, 
                    from_user_id=from_user_id, 
                    to_user_id=to_user_id,
                    image = image,
                    status= msg_status
                )
    

    message_data = {
        "type":"message",
        "data": created_message
    }

    await connection_manager.send_to_personal(to_user_id=message_data["data"]["to_user_id"], data=message_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"fail",
            "data": message_data
        }
    )


@router.get("/messages/{user_id}/unread")
async def get_unread_messages(user_id: int, db: Session = Depends(get_db)):
    
    messages = await get_unread_messages_service(db=db, user_id = user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data":messages
        }
    )


@router.get("/messages/{from_user_id}/with/{to_user_id}")
async def get_messages(from_user_id: int, to_user_id: int, db: Session = Depends(get_db)):
    
    messages = await get_messages_service(db=db, from_user_id=from_user_id, to_user_id=to_user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data":messages
        }
    )