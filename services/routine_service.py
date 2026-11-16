from fastapi import HTTPException

from models import Routine, User
from models.user_model import RolEnum
from repositories.routine_repository import RoutineRepository
from repositories.sport_profile_repository import SportProfileRepository
from repositories.user_repository import UserRepository
from schemas.routine_schema import RoutineCreate, RoutineUpdate


class RoutineService:
    def __init__(self, routine_repository: RoutineRepository, user_repository: UserRepository,
                 sport_profile_repository: SportProfileRepository):
        self.routine_repository = routine_repository
        self.user_repository = user_repository
        self.sport_profile_repository = sport_profile_repository

    def get_routine(self, routine_id: int, current_user: User) -> Routine | None:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        if routine.user_id != current_user.id and current_user.rol not in [RolEnum.PROFESOR, RolEnum.ADMIN]:
            raise HTTPException(status_code=403, detail="No tenés permisos para ver esta rutina")
        return routine

    def get_routines_by_user(self, user_id: int) -> list[Routine]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.routine_repository.get_by_user(user_id)

    def get_all_routines(self) -> list[Routine]:
        return self.routine_repository.get_all_routines()

    def create_routine(self, user_id: int, routine_data: RoutineCreate) -> Routine:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not self.sport_profile_repository.get_by_user(user_id):
            raise HTTPException(status_code=409, detail="El usuario no tiene un perfil deportivo")
        routine = Routine(**routine_data.model_dump())
        return self.routine_repository.create_new_routine(routine)

    def update_routine(self, routine_id: int, routine_data: RoutineUpdate) -> Routine:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        for campo, valor in routine_data.model_dump(exclude_unset=True).items():
            setattr(routine, campo, valor)
        return self.routine_repository.update_routine(routine)

    def delete_routine(self, routine_id: int) -> None:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        self.routine_repository.delete_routine(routine)
