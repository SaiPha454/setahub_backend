from fastapi import APIRouter, Depends, Body, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from services import user_service
from database_connection import get_db
from sqlalchemy.orm import Session
from schemas.user_shema import UserCreate, UserLogin, UserRead
from schemas.user_with_session_schema import UserReadWithTASession
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from fastapi.responses import Response
from fastapi.requests import Request
from pydantic import EmailStr, Field

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

protected_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(user_service.authenticate_user)]
)

@router.post("/register", response_model=dict)
async def register(
    db: Session = Depends(get_db),
    user : Annotated[UserCreate, Body()] = None
):
    if user == None :
        raise HTTPException(status_code=400, detail={
                 "message": "Invalid user data",
                 "status":"fail"
            }
         )
    else:
        created_user = await user_service.register(db, user)
        # print(created_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= {
                "data": {
                    "status":"success",
                    "data": created_user
                }
            }
        )
    
@router.post("/login", response_model=dict)
async def login(
    response: Response,
    db: Session = Depends(get_db),
    user : Annotated[UserLogin, Body()] = None,
):
    print("Requested", user)
    if user == None :
        raise HTTPException(status_code=400, detail="Bad request")
    else:

        logined_user = await user_service.login(db, user)
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "data": logined_user,
        
            }
        )
        response.set_cookie(
            key="jarvis",
            value=logined_user["access_token"],
            httponly=True
        )
        return response

@router.post("/reset-password",response_model=dict)
async def reset(
    response: Response,
    db: Session= Depends(get_db),
    email: EmailStr = Body(..., example="john.doe@example.com")
):
    await user_service.reset_password( db, email)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": "New password is reset successfully"
        }
    )
    return response

@protected_router.put("/change-password",response_model=dict)
async def reset(
    request: Request,
    response: Response,
    old_password: str = Body(..., min_length=8, example="strongpassword123"),
    new_password: str = Body(..., min_length=8, example="strongpassword123"),
    db: Session= Depends(get_db)
):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status":"fail",
                "data": "UnAthorized"
            }
        )
    user = await user_service.change_user_password_service(db, user_id, old_password=old_password, new_password=new_password)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {
            "status":"success",
            "data":user
        }
    )

@protected_router.get("/{user_id}", response_model=dict)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):

    result = await user_service.get_user_by_id_service(db, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )



@protected_router.put("/{user_id}/profile", response_model = dict)
async def update_profle_image(user_id: int , image: UploadFile = File(...), db: Session = Depends(get_db)  ):
    
    user = await user_service.update_profile_image_service(db, user_id= user_id, image= image)
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content={
            "status":"success",
            "data": user
        }
    )


@protected_router.put("/{user_id}", response_model=dict)
async def update_user_account(
        user_id: int, 
        name: str=Body(None), 
        email: str = Body(None),
        year: int = Body(None),
        student_id: int = Body(None),
        userbio : str = Body(None),
        db: Session = Depends(get_db) 
):
    user = await user_service.update_user_account_service(db=db, user_id=user_id, name=name, email=email, year=year, student_id=student_id, userbio=userbio)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data" : user
        }
    )


@protected_router.get("/{user_id}/registered-topics", response_model=dict)
async def get_user_by_id_with_registered_topics(user_id: int, db: Session = Depends(get_db)):
    
    result = await user_service.get_user_by_id_with_appointments_service(db, user_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )

@protected_router.get("/{user_id}/available-timeslots", response_model=dict)
async def get_user_available_timeslots(user_id: int, topic_id : int, db: Session = Depends(get_db)):
    
    result = await user_service.get_user_available_timeslots_service(db, user_id, topic_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )

@protected_router.get("/{user_id}/upcoming-bookings")
async def get_user_upcoming_booking(user_id: int, db: Session= Depends(get_db)):
    
    result = await user_service.get_user_upcoming_booking_service(db, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )

@protected_router.get("/{user_id}/completed-bookings")
async def get_user_completed_booking(user_id: int, db: Session= Depends(get_db)):
    result = await user_service.get_user_completed_booking_service(db, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )


@protected_router.get("/{user_id}/upcoming-appointments")
async def get_user_ta_upcoming_ta_appointments(user_id: int, db: Session= Depends(get_db)):
    result = await user_service.get_user_upcoming_ta_appointments_service(db, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )

@protected_router.get("/{user_id}/completed-appointments")
async def get_user_completed_ta_appointment(user_id: int, db: Session= Depends(get_db)):
    result = await user_service.get_user_completed_ta_appointments_service(db, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": result
        }
    )

@protected_router.post("/logout", response_model=dict)
async def user_logout(response: Response):
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success"
        }
    )

    response.delete_cookie(
        key="jarvis",  # Use the same key as when you set the cookie
        httponly=True,
        secure=True,  # Use this in production (requires HTTPS)
        samesite="strict"  # Adjust based on your application needs
    )
    return response



#example of protected user
@router.get("/", response_model=dict)
async def protected_route(
    request: Request,
    current_user: any = Depends(user_service.authenticate_user),
    db: Session = Depends(get_db),

):
    return current_user

    