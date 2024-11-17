
from pydantic import BaseModel
from typing import List
from .appointment_schema import AppointmentRead
from .topic_shema import TopicRead


class TopicRead(BaseModel):
    id: int
    img: str
    topic: str
    tas: int
    booked: int

    class Config:
        orm_mode = True  # This is important for converting SQLAlchemy models to Pydantic models
        from_attributes = True

class AppointmentRead(AppointmentRead):

    topic:TopicRead

    class Config:
        orm_mode = True
        from_attributes = True

class UserReadWithTASession(BaseModel):

    id: int
    name: str 
    email: str 
    year: int
    student_id: int
    appointments: List["AppointmentRead"]

    class Config:
        orm_mode = True
        from_attributes = True







