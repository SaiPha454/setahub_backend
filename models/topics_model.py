from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import Session, joinedload, relationship
from database_connection import Base
from fastapi import HTTPException, status
from typing import List, Optional
from models.appointment_model import Appointment
from models.booking_model import Booking

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    img = Column(Text)  # URL will be stored as text
    topic = Column(String(255))  # String with a max length of 255
    tas = Column(Integer)  # Integer value for 'tas'
    booked = Column(Integer)  # Integer value for 'booked'

    appointments = relationship("Appointment", back_populates="topic")
    bookings = relationship("Booking", back_populates="topic")

    def __repr__(self):
        return f"<Topic(id={self.id}, topic={self.topic}, tas={self.tas}, booked={self.booked})>"

# Create a new topic
def create_topic(db: Session, img: str, topic: str, tas: int =0, booked: int = 0) -> Topic:
    new_topic = Topic(img=img, topic=topic, tas=tas, booked=booked)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

# Read a topic by ID
def get_topic_by_id(db: Session, topic_id: int) -> Optional[Topic]:
    return db.query(Topic).filter(Topic.id == topic_id).first()


# Read a topic by ID
def get_topic_by_topic(db: Session, topic: str) -> Optional[Topic]:
    return db.query(Topic).filter(Topic.topic == topic).first()

# Read all topics
def get_all_topics(db: Session, skip: int = 0, limit: int = 10) -> List[Topic]:
    return db.query(Topic).offset(skip).limit(limit).all()


async def get_topic_with_sessions(db: Session, topic_id:int):
    topic = (
        db.query(Topic)
        .options(
            joinedload(Topic.appointments)
            .joinedload(Appointment.ta)
        )  # Preload related TASessions
        .filter(Topic.id == topic_id)
        .first()
    )
    return topic

# Update a topic by ID
async def update_topic(db: Session, topic_id: int, img: Optional[str] = None, topic: Optional[str] = None, 
                 tas: Optional[int] = None, booked: Optional[int] = None) -> Optional[Topic]:
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if db_topic:
        if img:
            db_topic.img = img
        if topic:
            db_topic.topic = topic
        if tas is not None:
            db_topic.tas = tas
        if booked is not None:
            db_topic.booked = booked
        db.commit()
        db.refresh(db_topic)
        return db_topic
    return None

# Delete a topic by ID
def delete_topic(db: Session, topic_id: int) -> bool:
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False