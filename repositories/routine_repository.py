from sqlalchemy.orm import Session

from models import Routine


class RoutineRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_new_routine(self, routine_create: Routine) -> Routine:
        self.db.add(routine_create)
        self.db.commit()
        self.db.refresh(routine_create)
        return routine_create

    def get_all_routines(self) -> list[Routine]:
        return self.db.query(Routine).all()

    def get_by_id(self, routine_id: int) -> Routine | None:
        return self.db.query(Routine).filter(Routine.id == routine_id).first()

    def get_by_user(self, user_id: int) -> list[Routine]:
        return self.db.query(Routine).filter(Routine.user_id == user_id).all()

    def update_routine(self, routine: Routine) -> Routine:
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def delete_routine(self, routine: Routine) -> None:
        self.db.delete(routine)
        self.db.commit()
