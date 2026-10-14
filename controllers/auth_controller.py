from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from repositories.user_repository import UserRepository
from schemas.user_schema import UserResponse, UserCreate
from services.auth_service import AuthService

router = APIRouter(prefix="/auth" , tags=["Auth"])


@router.post("/register" , response_model=UserResponse ,status_code=status.HTTP_201_CREATED)
def register(user: UserCreate , db : Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.register(user)




@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.login(form_data.username, form_data.password)
