from fastapi import HTTPException

from models import RoutineExercise
from repositories.exercise_repository import ExerciseRepository
from repositories.routine_exercise_repository import RoutineExerciseRepository
from repositories.routine_repository import RoutineRepository
from schemas.routine_exercise_schema import RoutineExerciseCreate, RoutineExerciseUpdate


class RoutineExerciseService:
    def __init__(self, routine_exercise_repository: RoutineExerciseRepository, routine_repository: RoutineRepository,
                 exercise_repository: ExerciseRepository):
        self.routine_exercise_repository = routine_exercise_repository
        self.routine_repository = routine_repository
        self.exercise_repository = exercise_repository

    def get_routine_exercise(self, routine_exercise_id: int) -> RoutineExercise:
        routine_exercise = self.routine_exercise_repository.get_by_id(routine_exercise_id)
        if not routine_exercise:
            raise HTTPException(status_code=404, detail="Routine exercise not found")
        return routine_exercise

    def create_routine_exercise(self, routine_id: int, routine_data: RoutineExerciseCreate) -> RoutineExercise:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")

        exercise = self.exercise_repository.get_by_id(routine_data.exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if self.routine_exercise_repository.exercise_exists_in_day(routine_id, routine_data.day,
                                                                   routine_data.exercise_id):
            raise HTTPException(status_code=409, detail="El ejercicio ya existe en esa rutina para ese día")

        if self.routine_exercise_repository.position_exists_in_day(routine_id, routine_data.day, routine_data.position):
            raise HTTPException(status_code=409, detail="La posición ya está ocupada para ese día")

        routine_exercise = RoutineExercise(routine_id=routine_id, **routine_data.model_dump())
        return self.routine_exercise_repository.create_routine_exercise(routine_exercise)

    def get_routine_exercises(self, routine_id: int) -> list[RoutineExercise]:
        routine = self.routine_repository.get_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        return self.routine_exercise_repository.get_by_routine_id(routine_id)



    def update_routine_exercise(
            self, routine_id: int, routine_exercise_id: int,
            routine_data: RoutineExerciseUpdate) -> RoutineExercise:

        routine_exercise = self.routine_exercise_repository.get_by_id(routine_exercise_id)
        if not routine_exercise or routine_exercise.routine_id != routine_id:
            raise HTTPException(status_code=404, detail="Routine exercise not found")

        data = routine_data.model_dump(exclude_unset=True)

        if "exercise_id" in data:
            exercise = self.exercise_repository.get_by_id(data["exercise_id"])
            if not exercise:
                raise HTTPException(status_code=404, detail="Exercise not found")

        new_day = data.get("day", routine_exercise.day)
        new_exercise_id = data.get("exercise_id", routine_exercise.exercise_id)
        new_position = data.get("position", routine_exercise.position)

        if "exercise_id" in data or "day" in data:
            if self.routine_exercise_repository.exercise_exists_in_day(routine_id, new_day, new_exercise_id,
                                                                       exclude_id=routine_exercise_id):
                raise HTTPException(status_code=409, detail="El ejercicio ya existe en esa rutina para ese día")

        if "position" in data or "day" in data:
            if self.routine_exercise_repository.position_exists_in_day(routine_id, new_day, new_position,
                                                                       exclude_id=routine_exercise_id):
                raise HTTPException(status_code=409, detail="La posición ya está ocupada para ese día")

        for campo, valor in data.items():
            setattr(routine_exercise, campo, valor)
        return self.routine_exercise_repository.update_routine_exercise(routine_exercise)


    def delete_routine_exercise(self, routine_id: int, routine_exercise_id: int) -> None:
        routine_exercise = self.routine_exercise_repository.get_by_id(routine_exercise_id)
        if not routine_exercise or routine_exercise.routine_id != routine_id:
            raise HTTPException(status_code=404, detail="Routine exercise not found")

        day = routine_exercise.day
        self.routine_exercise_repository.delete_routine_exercise(routine_exercise)

        exercises = self.routine_exercise_repository.get_by_routine_and_day(routine_id, day)
        for i, ex in enumerate(exercises, start=1):
            ex.position = i
        self.routine_exercise_repository.db.commit()
