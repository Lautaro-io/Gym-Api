from pydantic import BaseModel, Field
from typing import Optional
from models.enums import GrupoMuscularEnum


class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    muscular_group: GrupoMuscularEnum


class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    muscular_group: GrupoMuscularEnum

    class Config:
        from_attributes = True