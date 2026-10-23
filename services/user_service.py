from fastapi import HTTPException

from models import User
from models.enums import UserStateEnum
from repositories.user_repository import UserRepository
from schemas.user_schema import UserUpdate, UserRolUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_all_users(self) -> list[User]:
        return self.user_repository.get_all()

    def create_user(self, user: User) -> User:
        return self.user_repository.create(user)

    def update_user_rol(self, user_id: int, rol_update: UserRolUpdate) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not fousnd")

        user.rol = rol_update.rol
        return self.user_repository.update(user)

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        changes = data.model_dump(exclude_unset=True)

        for campo in ("email", "name", "lastname", "dni"):
            if campo in changes and changes[campo] is None:
                raise HTTPException(status_code=400, detail=f"El campo {campo} no puede ser null")

        if "email" in changes and changes["email"] != user.email:
            existing = self.user_repository.get_by_email(changes["email"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email")

        if "dni" in changes and changes["dni"] != user.dni:
            existing = self.user_repository.get_by_dni(changes["dni"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Ya existe un usuario con ese DNI")

        if changes.get("phone") is not None and changes["phone"] != user.phone:
            existing = self.user_repository.get_by_phone(changes["phone"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Ya existe un usuario con ese teléfono")

        for campo, valor in changes.items():
            setattr(user, campo, valor)

        return self.user_repository.update(user)

    def enable_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.state = UserStateEnum.HABILITADO_ENTRENAR
        return self.user_repository.update(user)

    def delete_user(self, user_id: int) -> None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.state = UserStateEnum.INACTIVO
        self.user_repository.update(user)
