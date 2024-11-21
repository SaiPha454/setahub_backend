
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    year: int = Field(..., ge=1, le=4, example=2024)
    student_id: int = Field(..., example=66011203)

    class Config:
        orm_mode = True
        from_attributes = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")

class UserAuthRead(UserBase):
    id: int = Field(..., example=1)
    access_token: Optional[str] = Field(None, example="jwt-token-string")
    userbio : str = ""
    image: str = ""
    class Config:
        orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., min_length=8, example="strongpassword123")


class UserRead(BaseModel):

    id: int
    name: str 
    email: str 
    year: int
    student_id: int
    userbio: str = ""
    image: str = ""

    class Config:
        orm_mode = True
        from_attributes = True








