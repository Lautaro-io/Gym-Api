from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.enums import RolEnum, UserStateEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=3, max_length=100)
    lastname: str = Field(..., min_length=3, max_length=100)
    dni: str = Field(..., min_length=7, max_length=8)
    phone: str = Field(..., min_length=9, max_length=15)



class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name :str
    lastname: str
    dni: str
    phone: Optional[str] = None
    rol: RolEnum
    state: UserStateEnum
    register_date: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRolUpdate(BaseModel):
    rol: RolEnum


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    lastname: Optional[str] = Field(None, min_length=3, max_length=100)
    dni: Optional[str] = Field(None, min_length=7, max_length=8)
    phone: Optional[str] = Field(None, min_length=9, max_length=15)
