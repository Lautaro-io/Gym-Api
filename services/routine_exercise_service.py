from fastapi import HTTPException

from models import RoutineExercise
from repositories.exercise_repository import ExerciseRepository
from repositories.routine_exercise_repository import RoutineExerciseRepository
from repositories.routine_repository import RoutineRepository
from schemas.routine_exercise_schema import RoutineExerciseCreate


class RoutineExerciseService:
    def __init__(self, routine_exercise_repository : RoutineExerciseRepository , routine_repository: RoutineRepository, exercise_repository : ExerciseRepository):
        self.routine_exercise_repository = routine_exercise_repository
        self.routine_repository = routine_repository
        self.exercise_repository = exercise_repository

    def get_routine_exercise(self, routine_exercise_id: int) -> RoutineExercise:
        routine_exercise = self.routine_exercise_repository.get_by_id(routine_exercise_id)
        if not routine_exercise:
            raise HTTPException(status_code=404, detail="Routine exercise not found")
        return routine_exercise

    def create_routine_exercise(self, routine_data : RoutineExerciseCreate) -> RoutineExercise:
        routine = self.routine_repository.get_by_id(routine_data.routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")

        exercise = self.exercise_repository.get_by_id(routine_data.exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        routine_exercise = RoutineExercise(**routine_data.model_dump())
        return self.routine_exercise_repository.create_routine_exercise(routine_exercise)

    def delete_routine_exercise(self, routine_exercise_id: int) -> None:
        routine_exercise = self.routine_exercise_repository.get_by_id(routine_exercise_id)
        if not routine_exercise:
            raise HTTPException(status_code=404, detail="Routine exercise not found")
        self.routine_exercise_repository.delete_routine_exercise(routine_exercise)




