from pydantic import BaseModel, EmailStr ,Field
from datetime import datetime
from models.enums import RolEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=3, max_length=100)
    lastname: str = Field(..., min_length=3, max_length=100)
    dni: str = Field(..., min_length=7, max_length=9)
    phone: str = Field(..., min_length=9, max_length=15)



class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name :str
    lastname: str
    dni: str
    phone: str
    rol: RolEnum
    active: bool
    register_date: datetime

    class Config:
        from_attributes = True