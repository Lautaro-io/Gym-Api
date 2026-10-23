from sqlalchemy.orm import Session

from models import Exercise
from models.enums import GrupoMuscularEnum


class ExerciseRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_new_exercise(self, exercise_create: Exercise) -> Exercise:
        self.db.add(exercise_create)
        self.db.commit()
        self.db.refresh(exercise_create)
        return exercise_create

    def get_all_exercises(self, muscular_group: GrupoMuscularEnum | None = None) -> list[Exercise]:
        query = self.db.query(Exercise)
        if muscular_group is not None:
            query = query.filter(Exercise.muscular_group == muscular_group)
        return query.all()

    def get_by_id(self, exercise_id: int) -> Exercise | None:
        return self.db.query(Exercise).filter(Exercise.id == exercise_id).first()

    def update_exercise(self, exercise: Exercise) -> Exercise:
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def delete_exercise(self, exercise: Exercise) -> None:
        self.db.delete(exercise)
        self.db.commit()

    def get_by_name(self, name: str) -> Exercise | None:
        return self.db.query(Exercise).filter(Exercise.name == name).first()
