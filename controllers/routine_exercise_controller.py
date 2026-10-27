from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.exercise_repository import ExerciseRepository
from repositories.routine_exercise_repository import RoutineExerciseRepository
from repositories.routine_repository import RoutineRepository
from schemas.routine_exercise_schema import (
    RoutineExerciseCreate,
    RoutineExerciseResponse,
    RoutineExerciseUpdate,
)
from security.jwt_service import get_current_user
from security.permissions import require_profesor
from services.routine_exercise_service import RoutineExerciseService

router = APIRouter(prefix="/routines", tags=["Routine Exercises"])


@router.post("/{id}/exercises", response_model=RoutineExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_routine_exercise(id: int, data: RoutineExerciseCreate, current_user: User = Depends(require_profesor),
                            db: Session = Depends(get_db)) -> RoutineExerciseResponse:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    return routine_exercise_service.create_routine_exercise(id, data)


@router.get("/{id}/exercises", response_model=list[RoutineExerciseResponse])
def get_routine_exercises(id: int, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)) -> list[RoutineExerciseResponse]:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    return routine_exercise_service.get_routine_exercises(id)


@router.patch("/{id}/exercises/{re_id}", response_model=RoutineExerciseResponse)
def update_routine_exercise(id: int, re_id: int, data: RoutineExerciseUpdate,
                            current_user: User = Depends(require_profesor),
                            db: Session = Depends(get_db)) -> RoutineExerciseResponse:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    return routine_exercise_service.update_routine_exercise(id, re_id, data)


@router.delete("/{id}/exercises/{re_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_exercise(id: int, re_id: int, current_user: User = Depends(require_profesor),
                            db: Session = Depends(get_db)) -> None:
    routine_exercise_service = RoutineExerciseService(
        RoutineExerciseRepository(db), RoutineRepository(db), ExerciseRepository(db)
    )
    routine_exercise_service.delete_routine_exercise(id, re_id)
