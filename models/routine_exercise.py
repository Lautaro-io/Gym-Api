from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from db import Base

class RoutineExercise(Base):
    __tablename__ = "routine_exercise"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routine.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    day = Column(String(10), nullable=False)
    sets = Column(Integer, nullable=False)
    repetitions = Column(String(20), nullable=False)
    position = Column(Integer, nullable=False)
    rest = Column(Integer, nullable=False)

    routine = relationship("Routine", back_populates="exercises")

    exercise = relationship("Exercise", back_populates="routines")