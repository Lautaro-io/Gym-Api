from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from models.enums import GrupoMuscularEnum
from repositories.exercise_repository import ExerciseRepository
from schemas.exercise_schema import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from security.jwt_service import get_current_user
from security.permissions import require_profesor
from services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> ExerciseResponse:
    exercise_service = ExerciseService(ExerciseRepository(db))
    return exercise_service.create_exercise(exercise_data)


@router.get("", response_model=list[ExerciseResponse])
def get_exercises(
    muscular_group: GrupoMuscularEnum | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExerciseResponse]:
    exercise_service = ExerciseService(ExerciseRepository(db))
    return exercise_service.get_all_exercises(muscular_group)


@router.get("/{id}", response_model=ExerciseResponse)
def get_exercise(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExerciseResponse:
    exercise_service = ExerciseService(ExerciseRepository(db))
    return exercise_service.get_exercise(id)


@router.patch("/{id}", response_model=ExerciseResponse)
def update_exercise(
    id: int,
    exercise_data: ExerciseUpdate,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> ExerciseResponse:
    exercise_service = ExerciseService(ExerciseRepository(db))
    return exercise_service.update_exercise(id, exercise_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    id: int,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> None:
    exercise_service = ExerciseService(ExerciseRepository(db))
    exercise_service.delete_exercise(id)
