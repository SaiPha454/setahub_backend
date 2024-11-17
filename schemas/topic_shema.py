from pydantic import BaseModel
from typing import Optional
from fastapi import Form, File, UploadFile


class TopicRead(BaseModel):
    id: int
    img: str
    topic: str
    tas: int
    booked: int

    class Config:
        orm_mode = True  # This is important for converting SQLAlchemy models to Pydantic models
        from_attributes = True


class TopicUpdate(BaseModel):
    img: Optional[str] = None
    topic: Optional[str] = None
    tas: Optional[int] = None
    booked: Optional[int] = None

    class Config:
        orm_mode = True  # This is important for converting SQLAlchemy models to Pydantic models
        from_attributes = True


class TopicCreate(BaseModel):
    img: UploadFile = File(...)
    topic: str = Form(...)
