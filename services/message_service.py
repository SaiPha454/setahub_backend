from fastapi import HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from schemas.message_schema import MessageRead
from models.message_model import create_message_model, get_messages_model, get_unread_messages_model
from services.user_service import get_user_by_id_service
from schemas.user_shema import UserRead
import uuid
import shutil
from pathlib import Path


# Define directory to store uploaded images
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)  # Create the directory if it doesn't exist


async def create_message_service(db: Session, from_user_id: int, to_user_id: int, message: str, msg_type : str, status: str):
   
    message = await create_message_model(db, from_user_id = from_user_id, to_user_id = to_user_id, message = message, msg_type = msg_type, status=status)
    
    message = MessageRead.model_validate(message).model_dump()
    message["timestamp"] = message["timestamp"].strftime("%Y-%m-%d %I:%M %p")

    # message["from_user"] = await get_user_by_id_service(db=db, user_id= message["from_user_id"])
    # message["to_user"] = await get_user_by_id_service(db=db, user_id= message["to_user_id"])
    return message


async def get_messages_service(db: Session, from_user_id: int, to_user_id: int):

    messages = await get_messages_model(db=db, from_user_id=from_user_id, to_user_id=to_user_id)
    result = []

    for message in messages:
        if message.to_user_id == from_user_id and message.status == "sent":
            message.status = 'read'
        msg = MessageRead.model_validate(message).model_dump()
        msg["timestamp"] = msg["timestamp"].strftime("%Y-%m-%d %I:%M %p")
        result.append(msg)
    db.commit()
    return result


async def get_unread_messages_service(db: Session, user_id: int):
    messages = await get_unread_messages_model(db=db, user_id = user_id)
    result = []

    for message in messages:

        msg = MessageRead.model_validate(message).model_dump()
        msg["timestamp"] = msg["timestamp"].strftime("%Y-%m-%d %I:%M %p")
        result.append(msg)
    return result


async def create_message_image_service(request: Request, db: Session, from_user_id: int, to_user_id: int, image: UploadFile, status: str):



    try:
        # Generate a unique filename for the image
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        img_path = IMAGE_DIR / unique_filename

        # Save the uploaded file with the unique filename
        with img_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Create the URL for the saved image
        img_url =  f"{request.base_url}images/{unique_filename}"

        message = await create_message_model(db, from_user_id = from_user_id, to_user_id = to_user_id, message = img_url, msg_type = "image", status=status)
        
        message = MessageRead.model_validate(message).model_dump()
        message["timestamp"] = message["timestamp"].strftime("%Y-%m-%d %I:%M %p")

        return message

    except Exception as e:
        # Rollback in case of any error and raise an HTTPException
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status":"fail",
                "message":"An error occurred while sending the image"
            }
        )