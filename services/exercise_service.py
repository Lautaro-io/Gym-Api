from fastapi import HTTPException

from models import Exercise
from models.enums import GrupoMuscularEnum
from repositories.exercise_repository import ExerciseRepository
from schemas.exercise_schema import ExerciseCreate, ExerciseUpdate


class ExerciseService:
    def __init__(self, exercise_repository: ExerciseRepository):
        self.exercise_repository = exercise_repository

    def get_exercise(self, exercise_id: int) -> Exercise | None:
        exercise = self.exercise_repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return exercise

    def get_all_exercises(self, muscular_group: GrupoMuscularEnum | None = None) -> list[Exercise]:
        return self.exercise_repository.get_all_exercises(muscular_group)

    def create_exercise(self, exercise_data: ExerciseCreate) -> Exercise:
        if self.exercise_repository.get_by_name(exercise_data.name):
            raise HTTPException(status_code=409, detail=f"El ejercicio con el nombre '{exercise_data.name}' ya existe.")
        exercise = Exercise(**exercise_data.model_dump())
        return self.exercise_repository.create_new_exercise(exercise)

    def update_exercise(self, exercise_id: int, exercise_data: ExerciseUpdate) -> Exercise:
        exercise = self.exercise_repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        for campo, valor in exercise_data.model_dump(exclude_unset=True).items():
            setattr(exercise, campo, valor)
        return self.exercise_repository.update_exercise(exercise)

    def delete_exercise(self, exercise_id: int) -> None:
        exercise = self.exercise_repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        self.exercise_repository.delete_exercise(exercise)
