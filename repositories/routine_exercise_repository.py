from sqlalchemy.orm import Session
from models import RoutineExercise

class RoutineExerciseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_routine_exercise(self, routineExercise: RoutineExercise) -> RoutineExercise:
        self.db.add(routineExercise)
        self.db.commit()
        self.db.refresh(routineExercise)
        return routineExercise

    def get_by_id(self, routine_exercise_id: int) -> RoutineExercise | None:
        return self.db.query(RoutineExercise).filter(RoutineExercise.id == routine_exercise_id).first()

    def get_by_routine_id(self, routine_id: int) -> list[RoutineExercise]:
        return self.db.query(RoutineExercise).filter(RoutineExercise.routine_id == routine_id).all()

    def delete_routine_exercise(self, routine_exercise) -> None:
        self.db.delete(routine_exercise)
        self.db.commit()