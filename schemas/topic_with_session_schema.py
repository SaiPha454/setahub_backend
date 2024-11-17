from pydantic import BaseModel
from typing import Optional
from fastapi import Form, File, UploadFile
from typing import List
from .user_shema import UserRead
from schemas.appointment_schema import AppointmentRead


class AppointmentTopicRead(AppointmentRead):

    ta: Optional[UserRead]

    class Config:
        orm_mode = True
        from_attributes = True


class TopicReadWithAppointments(BaseModel):
    id: int
    img: str
    topic: str
    tas: int
    booked: int

    appointments: List[AppointmentTopicRead]

    class Config:
        orm_mode = True