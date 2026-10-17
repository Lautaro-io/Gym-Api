from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserResponse, UserUpdate
from security.jwt_service import get_current_user
from security.permissions import require_admin
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> UserResponse:
    return UserService(UserRepository(db)).get_user(id)


@router.get("", response_model=list[UserResponse])
def get_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserResponse]:
    return UserService(UserRepository(db)).get_all_users()

@router.patch("/{id}", response_model=UserResponse)
def update_user(id: int, user_update: UserUpdate, current_user: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> UserResponse:
    user_service = UserService(UserRepository(db))
    updated_user = user_service.update_user(id, user_update)
    return updated_user


@router.patch("/{id}/habilitar", response_model=UserResponse)
def enable_user(id: int, current_user: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> UserResponse:
    return UserService(UserRepository(db)).enable_user(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, current_user: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> None:
    UserService(UserRepository(db)).delete_user(id)
