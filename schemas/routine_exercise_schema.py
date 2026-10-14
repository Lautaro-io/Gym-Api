from pydantic import BaseModel, ConfigDict, Field


class RoutineExerciseCreate(BaseModel):
    routine_id: int = Field(..., gt=0)
    exercise_id: int = Field(..., gt=0)
    day: str = Field(..., min_length=1, max_length=10)
    sets: int = Field(..., gt=0)
    repetitions: str = Field(..., min_length=1, max_length=20)
    position: int = Field(..., gt=0)
    rest: int = Field(..., ge=0)


class RoutineExerciseResponse(BaseModel):
    id: int
    routine_id: int
    exercise_id: int
    day: str
    sets: int
    repetitions: str
    position: int
    rest: int

    model_config = ConfigDict(from_attributes=True)