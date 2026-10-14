from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SportProfileCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    goal: str = Field(..., min_length=3, max_length=100)
    level: str = Field(..., min_length=3, max_length=50)
    days_per_week: int = Field(..., gt=0, le=7)
    session_duration: int = Field(..., gt=0) # in minutes
    age: int = Field(..., gt=10, le=100)
    injuries: Optional[str] = Field(None, max_length=255)
    trainer_tracking: bool = False

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

    model_config = ConfigDict(from_attributes=True)