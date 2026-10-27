from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserResponse, UserCreate, UserPasswordUpdate
from security.jwt_service import get_current_user
from services.auth_service import AuthService

router = APIRouter(prefix="/auth" , tags=["Auth"])


@router.post("/register" , response_model=UserResponse ,status_code=status.HTTP_201_CREATED)
def register(user: UserCreate , db : Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.register(user)


@router.patch("/password" , response_model=UserResponse ,status_code=status.HTTP_200_OK)
def update_password(data : UserPasswordUpdate, current_user: User = Depends(get_current_user), db : Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    user = service.update_password(current_user.id, data.old_password, data.new_password)
    return user




@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.login(form_data.username, form_data.password)
