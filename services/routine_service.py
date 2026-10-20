from fastapi import HTTPException

from models import Routine
from repositories.routine_repository import RoutineRepository
from repositories.user_repository import UserRepository
from schemas.routine_schema import RoutineCreate, RoutineUpdate


class RoutineService:
    def __init__(self, routine_repository: RoutineRepository, user_repository: UserRepository):
        self.routine_repository = routine_repository
        self.user_repository = user_repository

    def get_routine(self, routine_id: int) -> Routine | None:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
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
