from sqlalchemy import Column, ForeignKey, Integer, Date
from sqlalchemy.orm import relationship, Session, joinedload
from database_connection import Base
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from sqlalchemy.dialects.postgresql import JSONB
from schemas.appointment_schema import AppointmentCreate
# from .topics_model import Topic

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    ta_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    date = Column(JSONB, nullable=True)
    timeslots = Column(JSONB, nullable=True)

    # Relationship with Topic
    topic = relationship("Topic", back_populates="appointments")
    ta = relationship("User", back_populates="appointments")
    



async def create_appointment_model(db: Session, data : AppointmentCreate) -> Appointment:
    try:
        new_appointment = Appointment(
            topic_id=data.topic_id,
            ta_id=data.ta_id,
            date=data.date,
            timeslots=data.timeslots
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Failed to create Appointment due to internal server error"
            }
        )
    

async def get_appointment_by_topic_id_and_ta_id_model(db: Session, topic_id: int,ta_id:int) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.topic_id == topic_id, Appointment.ta_id == ta_id).first()
    return appointment


async def get_appointment_by_id_model(db: Session, appointment_id: int) -> Appointment:
    appointment = ( 
        db.query(Appointment)
        .options(
            joinedload(Appointment.topic),
            joinedload(Appointment.ta)
        )
        .filter(Appointment.id == appointment_id).first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'status':"fail",
                "message":f"Appointment with ID {appointment_id} not found"
            }
        )
    topic = appointment.topic
    if topic.tas > 0 :
        topic.tas = topic.tas -1
        db.commit()
        db.refresh(topic)
    print(topic)
    return appointment

async def update_appointment_model(
    db: Session,
    appointment_id: int,
    date: List[str] = None,
    timeslots: Optional[Dict] = None
) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'status':"fail",
                "message":f"Appointment with ID {appointment_id} not found"
            }
        )
    try:
        if date is not None:
            appointment.date = date
        if timeslots is not None:
            appointment.timeslots = timeslots

        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Failed to update Appointment due to internal server error"
            }
        )


async def delete_appointment_model(db: Session, appointment_id: int) -> bool:
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    try:
        db.delete(appointment)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Failed to delete Appointment due to internal server error"
            }
        )

