from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.routine_repository import RoutineRepository
from repositories.user_repository import UserRepository
from schemas.routine_schema import (
    RoutineCreate,
    RoutineDetailResponse,
    RoutineResponse,
    RoutineUpdate,
)
from security.jwt_service import get_current_user
from security.permissions import require_profesor
from services.routine_service import RoutineService

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.post("", response_model=RoutineResponse, status_code=status.HTTP_201_CREATED)
def create_routine(
    routine_data: RoutineCreate,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> RoutineResponse:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    return routine_service.create_routine(routine_data.user_id, routine_data)


@router.get("", response_model=list[RoutineResponse])
def get_routines(
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> list[RoutineResponse]:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    return routine_service.get_all_routines()


@router.get("/me", response_model=list[RoutineDetailResponse])
def get_my_routines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RoutineDetailResponse]:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    return routine_service.get_routines_by_user(current_user.id)


@router.get("/{id}", response_model=RoutineDetailResponse)
def get_routine(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoutineDetailResponse:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    return routine_service.get_routine(id)


@router.patch("/{id}", response_model=RoutineResponse)
def update_routine(
    id: int,
    routine_data: RoutineUpdate,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> RoutineResponse:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    return routine_service.update_routine(id, routine_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(
    id: int,
    current_user: User = Depends(require_profesor),
    db: Session = Depends(get_db),
) -> None:
    routine_service = RoutineService(RoutineRepository(db), UserRepository(db))
    routine_service.delete_routine(id)
