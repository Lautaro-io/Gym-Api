from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserResponse
from security.jwt_service import get_current_user
from security.permissions import require_admin
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def get_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserResponse]:
    return UserService(UserRepository(db)).get_all_users()


@router.get("{id}", response_model=UserResponse)
def get_user(id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> UserResponse:
    user = UserService(UserRepository(db)).get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
