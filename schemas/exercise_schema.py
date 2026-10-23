from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.enums import GrupoMuscularEnum


class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    muscular_group: GrupoMuscularEnum


class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    muscular_group: Optional[GrupoMuscularEnum] = None


class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    muscular_group: GrupoMuscularEnum

    model_config = ConfigDict(from_attributes=True)
