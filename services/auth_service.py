from fastapi import HTTPException
from starlette import status

from models import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate
from security.jwt_service import create_access_token
from services.password_service import hash_password, verify_password


class AuthService:

    def __init__(self, user_repository : UserRepository):
        self.user_repository = user_repository

    def register(self, data : UserCreate) -> User:
        if self.user_repository.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email"
            )

        if self.user_repository.get_by_dni(data.dni):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese DNI"
            )
        if self.user_repository.get_by_phone(data.phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese teléfono"
            )

        user = User(
            dni=data.dni,
            name=data.name,
            lastname=data.lastname,
            phone=data.phone,
            email=data.email,
            hashed_password=hash_password(data.password)
        )

        return self.user_repository.create(user)


    def login(self, email: str, password: str) -> dict[str, str]:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta"
            )

        token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": token,
            "token_type": "bearer"
        }

