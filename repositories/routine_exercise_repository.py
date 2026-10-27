from sqlalchemy.orm import Session, selectinload
from models import RoutineExercise
from models.enums import DiaSemanaEnum


class RoutineExerciseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_routine_exercise(self, routine_exercise: RoutineExercise) -> RoutineExercise:
        self.db.add(routine_exercise)
        self.db.commit()
        self.db.refresh(routine_exercise)
        return routine_exercise

    def get_by_id(self, routine_exercise_id: int) -> RoutineExercise | None:
        return self.db.query(RoutineExercise).filter(RoutineExercise.id == routine_exercise_id).first()

    def get_by_routine_id(self, routine_id: int) -> list[RoutineExercise]:
        return (
            self.db.query(RoutineExercise)
            .options(selectinload(RoutineExercise.exercise))
            .filter(RoutineExercise.routine_id == routine_id)
            .order_by(RoutineExercise.day, RoutineExercise.position)
            .all()
        )

    def get_by_routine_and_day(self, routine_id: int, day: DiaSemanaEnum) -> list[RoutineExercise]:
        return (
            self.db.query(RoutineExercise)
            .filter(RoutineExercise.routine_id == routine_id, RoutineExercise.day == day.value)
            .order_by(RoutineExercise.position)
            .all()
        )

    def exercise_exists_in_day(self, routine_id: int, day: DiaSemanaEnum, exercise_id: int, exclude_id: int | None = None) -> bool:
        query = self.db.query(RoutineExercise).filter(
            RoutineExercise.routine_id == routine_id,
            RoutineExercise.day == day.value,
            RoutineExercise.exercise_id == exercise_id,
        )
        if exclude_id is not None:
            query = query.filter(RoutineExercise.id != exclude_id)
        return query.first() is not None

    def position_exists_in_day(self, routine_id: int, day: DiaSemanaEnum, position: int, exclude_id: int | None = None) -> bool:
        query = self.db.query(RoutineExercise).filter(
            RoutineExercise.routine_id == routine_id,
            RoutineExercise.day == day,
            RoutineExercise.position == position,
        )
        if exclude_id is not None:
            query = query.filter(RoutineExercise.id != exclude_id)
        return query.first() is not None

    def update_routine_exercise(self, routine_exercise: RoutineExercise) -> RoutineExercise:
        self.db.commit()
        self.db.refresh(routine_exercise)
        return routine_exercise

    def delete_routine_exercise(self, routine_exercise: RoutineExercise) -> None:
        self.db.delete(routine_exercise)
        self.db.commit()