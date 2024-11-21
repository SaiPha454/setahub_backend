from sqlalchemy import Column, String, Integer, UniqueConstraint, Text
from sqlalchemy.orm import Session, relationship, joinedload
from database_connection import Base
from fastapi import HTTPException, status
from models.appointment_model import Appointment
from schemas.user_shema import UserCreate
from .booking_model import Booking


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    year = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)  # Hashed password
    access_token = Column(String(500), nullable=True)  # Token for login (e.g., JWT)
    userbio = Column(String(500), nullable=True, default="")
    image = Column(String(500), nullable = True, default = "/images/profile.svg")

    
    appointments = relationship("Appointment", back_populates="ta")
    student_bookings = relationship("Booking", foreign_keys=[Booking.student_id], back_populates="student")
    ta_bookings = relationship("Booking", foreign_keys=[Booking.ta_id], back_populates="ta")
    # Define relationships for sent and received messages
    sent_messages = relationship("Message", back_populates="from_user", foreign_keys="Message.from_user_id")
    received_messages = relationship("Message", back_populates="to_user", foreign_keys="Message.to_user_id")

async def create_user_account_model(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        year=user.year,
        student_id=user.student_id,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def update_user_account_model(
        db: Session, 
        user_id: int, 
        name: str=None, 
        email: str = None,
        year: int = None,
        student_id: int = None,
        userbio : str = None
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail",
                "message" : "User account does not exist"
            }
        )
    
    
    if name:
        user.name = name
    if email:
        email_user = db.query(User).filter(User.id != user_id, User.email == email).first()
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "fail",
                    "message" : "User with this email already exist. Email must be unique"
                }
        )
        user.email = email
    if year:
        user.year = year
    if student_id:
        student_user = db.query(User).filter(User.id != user_id, User.student_id == student_id).first()
        if student_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "fail",
                    "message" : "User with this stduent id already exist. Student ID must be unique."
                }
        )
        user.student_id = student_id
    if userbio:
        user.userbio = userbio
    
    db.commit()
    db.refresh(user)
    return user

async def update_user_token(db: Session, user_email: str, user_token: str):

    user = await get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message":"User does not exist"
            }
        )
    user.access_token = user_token
    return user

async def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id== user_id).first()

async def get_user_by_id_with_appointments_model(db: Session, user_id: int):
    return (db.query(User)
        .options(joinedload(User.appointments). joinedload(Appointment.topic))
        .filter(User.id == user_id)
        .first()
    )

async def get_user_by_email(db: Session, user_email: str):
    return db.query(User).filter(User.email== user_email).first()

async def get_user_by_token(db: Session, user_token: str):
    return db.query(User).filter(User.access_token==user_token).first()