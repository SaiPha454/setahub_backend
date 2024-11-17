from sqlalchemy.orm import Session
from schemas.user_shema import UserCreate, UserAuthRead, UserLogin, UserRead
from models.users_model import User
from models import users_model
from utils.security import hash_password, verify_password, create_access_token
from utils import mail, security
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from fastapi import Depends
from database_connection import get_db
import random, string
from models.users_model import create_user_account_model
from schemas.user_with_session_schema import UserReadWithTASession
from models import booking_model, appointment_model
from schemas.booking_detail_schema import BookingReadWithTopicAndTA, BookingReadWithTopicAndStudent
from .appointment_service import get_appointment_by_topic_and_ta_service


async def register(db: Session, user: UserCreate) -> dict:
    
    try:
        user.password = hash_password(user.password)  # Hash the password
        db_user =await create_user_account_model(db, user)

        result = UserAuthRead.model_validate(db_user)
        
        result= UserAuthRead.model_dump(result)
        print("User : ",result)
        return result
    
    except IntegrityError:
        db.rollback()  # Rollback the transaction on error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= {
                "error": {
                    "message": "The user already exist"
                }
            }
        )
    
    except SQLAlchemyError as e:
        print(e)
        db.rollback()  # Rollback for other SQLAlchemy errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= {
                "error": {
                    "message": "Internal server error while creating the account"
                }
            }
        )


async def login(db: Session, user: UserLogin):
    
    userdb = await validate_email_and_password(db, user.email, user.password)
    if type(userdb) != User :
        return userdb

    access_token = create_access_token(
        data={
            "user_id":userdb.id,
            "student_id:": userdb.student_id,
            "email":userdb.email
        }
    )
    
    userdb.access_token = access_token
    db.commit()
    db.refresh(userdb)

    return UserAuthRead.model_validate(userdb).model_dump()
    

async def reset_password(db, email: str):

    userdb = await users_model.get_user_by_email(db,email)
    if userdb == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message": "This email is not registered yet"
                
            }
        )
    
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    userdb.password = security.hash_password(random_string)
    db.commit()
    db.refresh(userdb)
    await mail.send_email(email, random_string)


    
async def change_user_password_service(db: Session, user_id:int, old_password: str, new_password: str):
    
    userdb = await users_model.get_user_by_id(db, user_id=user_id)
    
    if not userdb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":f"User with ID {user_id} does not exist"
            }
        )
    if not verify_password(old_password, userdb.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "message": "old password is not correct",
                    "status":"fail"
                }
            }
        )
    userdb.password = hash_password(new_password)
    db.commit()
    db.refresh(userdb)
    return UserRead.model_validate(userdb).model_dump()


async def get_user_by_id_service(db: Session, user_id: int):
    user = await users_model.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        )
    user= UserRead.model_validate(user).model_dump()
    return user

async def get_user_by_id_with_appointments_service(db: Session, user_id: int):
    
    user = await users_model.get_user_by_id_with_appointments_model(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        )
    return UserReadWithTASession.model_validate(user).model_dump()


async def get_user_available_timeslots_service(db: Session, user_id: int, topic_id: int):
    
    all_timeslots = await get_appointment_by_topic_and_ta_service(db, topic_id, user_id)
    all_timeslots = all_timeslots["timeslots"]
    
    upcoming_appointments = await get_user_upcoming_ta_appointments_service(db, user_id=user_id)
    booked_timeslots = {}
    for appointment in upcoming_appointments:
        if appointment["date"] in booked_timeslots:
            booked_timeslots[appointment["date"]].append(appointment["timeslot"])
        else:
            booked_timeslots[appointment["date"]] = [appointment["timeslot"]]
    
    available_timeslots = all_timeslots
    for date in available_timeslots:

        i = 0  # Index to keep track of the position in the list
        while i < len(available_timeslots[date]):
            timeslot = available_timeslots[date][i]
            if timeslot in booked_timeslots.get(date, []):
                available_timeslots[date].remove(timeslot)
            else:
                i += 1  # Only increment the index if no removal was done
    
    return available_timeslots



async def get_user_upcoming_booking_service(db: Session, user_id: int):

    user = await users_model.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        )
    
    bookings = await booking_model.get_student_upcoming_bookings_model(db, user_id)
 
    results = []
    for booking in bookings:
        booking.date = booking.date.strftime("%Y-%m-%d")
        results.append(BookingReadWithTopicAndTA.model_validate(booking).model_dump())
    
    return results

async def get_user_completed_booking_service(db: Session, user_id: int):
    
    user = await users_model.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        )
    
    bookings = await booking_model.get_student_completed_bookings_model(db, user_id)
 
    results = []
    for booking in bookings:
        booking.date = booking.date.strftime("%Y-%m-%d")
        results.append(BookingReadWithTopicAndTA.model_validate(booking).model_dump())
    
    return results

async def get_user_upcoming_ta_appointments_service(db: Session, user_id: int):
    
   
    user = await users_model.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        )


    bookings = await booking_model.get_ta_upcoming_appointments_model(db, user_id)
 
    results = []
    for booking in bookings:
        booking.date = booking.date.strftime("%Y-%m-%d")
        results.append(BookingReadWithTopicAndStudent.model_validate(booking).model_dump())
    
    return results

async def get_user_completed_ta_appointments_service(db: Session, user_id: int):
    
    
    user = await users_model.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":"User does not exist"
            }
        ) 
    
    bookings = await booking_model.get_ta_completed_appointments_model(db, user_id)
 
    results = []
    for booking in bookings:
        booking.date = booking.date.strftime("%Y-%m-%d")
        results.append(BookingReadWithTopicAndStudent.model_validate(booking).model_dump())
    
    return results



async def validate_email_and_password(db: Session, user_email:str, user_password: str):
    
    userdb = await users_model.get_user_by_email(db,user_email)
    if userdb == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "message": "user does not exist",
                    "status":"fail"
                }
            }
        )
    if(verify_password(user_password, userdb.password) == False) :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "message": "password is not correct",
                    "status":"fail"
                }
            }
        )
    return userdb

async def validate_token(db: Session, user_token : str):

    user = await users_model.get_user_by_token(db, user_token)
    if not user :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message":"Invalid Token",
                "detail":None
            }
        )
    return user


async def authenticate_user( request: Request,db: Session= Depends(get_db)):
    token = await security.get_token_from_cookie(request,"jarvis")
    user = await validate_token(db,token)
    return user