import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SportProfileCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    goal: str = Field(..., min_length=3, max_length=100)
    level: str = Field(..., min_length=3, max_length=50)
    days_per_week: int = Field(..., gt=0, le=7)
    session_duration: int = Field(..., gt=0)
    age: int = Field(..., gt=10, le=100)
    injuries: Optional[str] = Field(None, max_length=255)
    trainer_tracking: bool = False

class SportProfileUpdate(BaseModel):
    goal: Optional[str] = Field(None, min_length=3, max_length=100)
    level: Optional[str] = Field(None, min_length=3, max_length=50)
    days_per_week: Optional[int] = Field(None, gt=0, le=7)
    session_duration: Optional[int] = Field(None, gt=0)
    age: Optional[int] = Field(None, gt=10, le=100)
    injuries: Optional[str] = Field(None, max_length=255)
    trainer_tracking: Optional[bool] = None

class SportProfileResponse(BaseModel):
    id: int
    user_id: int
    goal: str
    level: str
    days_per_week: int
    session_duration: int
    age: int
    injuries: Optional[str]
    trainer_tracking: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)