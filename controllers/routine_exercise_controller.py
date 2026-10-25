from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.exercise_repository import ExerciseRepository
from repositories.routine_exercise_repository import RoutineExerciseRepository
from repositories.routine_repository import RoutineRepository
from schemas.routine_exercise_schema import RoutineExerciseCreate, RoutineExerciseResponse
from security.permissions import require_profesor
from services.routine_exercise_service import RoutineExerciseService

router = APIRouter(prefix="/routine-exercises", tags=["Routine Exercises"])


@router.post("", response_model=RoutineExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_routine_exercise(data: RoutineExerciseCreate, current_user: User = Depends(require_profesor),
                            db: Session = Depends(get_db)) -> RoutineExerciseResponse:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    return routine_exercise_service.create_routine_exercise(data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_exercise(id: int, current_user: User = Depends(require_profesor),
                            db: Session = Depends(get_db)) -> None:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    routine_exercise_service.delete_routine_exercise(id)