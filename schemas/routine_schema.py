from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from models.enums import DiaSemanaEnum
from schemas.exercise_schema import ExerciseResponse


class RoutineCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    date_generated: date
    state: bool = True


class RoutineUpdate(BaseModel):
    date_generated: Optional[date] = None
    state: Optional[bool] = None


class RoutineResponse(BaseModel):
    id: int
    user_id: int
    date_generated: date
    state: bool

    model_config = ConfigDict(from_attributes=True)


class RoutineExerciseDetail(BaseModel):
    id: int
    day: DiaSemanaEnum
    sets: int
    repetitions: str
    position: int
    rest: int
    exercise: ExerciseResponse

    model_config = ConfigDict(from_attributes=True)


class RoutineDetailResponse(BaseModel):
    id: int
    user_id: int
    date_generated: date
    state: bool
    exercises: List[RoutineExerciseDetail]

    model_config = ConfigDict(from_attributes=True)
