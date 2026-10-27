from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.enums import DiaSemanaEnum


class RoutineExerciseCreate(BaseModel):
    exercise_id: int = Field(..., gt=0)
    day: DiaSemanaEnum
    sets: int = Field(..., gt=0)
    repetitions: str = Field(..., min_length=1, max_length=20)
    position: int = Field(..., gt=0)
    rest: int = Field(..., ge=0, description="Segundos de descanso")


class RoutineExerciseUpdate(BaseModel):
    exercise_id: Optional[int] = Field(None, gt=0)
    day: Optional[DiaSemanaEnum] = None
    sets: Optional[int] = Field(None, gt=0)
    repetitions: Optional[str] = Field(None, min_length=1, max_length=20)
    position: Optional[int] = Field(None, gt=0)
    rest: Optional[int] = Field(None, ge=0, description="Segundos de descanso")


class RoutineExerciseResponse(BaseModel):
    id: int
    routine_id: int
    exercise_id: int
    day: DiaSemanaEnum
    sets: int
    repetitions: str
    position: int
    rest: int

    model_config = ConfigDict(from_attributes=True)