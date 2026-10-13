from typing import List

from pydantic import BaseModel, Field
from datetime import date


class RoutineCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    date_generated: date
    state: bool = True


class RoutineResponse(BaseModel):
    id: int
    user_id: int
    date_generated: date
    state: bool

    class Config:
        from_attributes = True



class RoutineExerciseDetail(BaseModel):
    id: int
    day: str
    sets: int
    repetitions: str
    position: int
    rest: int
    exercise_id: int

    class Config:
        from_attributes = True


class RoutineDetailResponse(BaseModel):
    id: int
    user_id: int
    date_generated: date
    state: bool
    exercises: List[RoutineExerciseDetail]

    class Config:
        from_attributes = True