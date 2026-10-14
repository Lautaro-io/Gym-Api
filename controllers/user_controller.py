from fastapi import APIRouter, Depends

from models import User
from schemas.user_schema import UserResponse
from security.jwt_service import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user