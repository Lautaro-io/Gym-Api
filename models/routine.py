from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from db import Base


class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date_generated = Column(Date, nullable=False)
    state = Column(Boolean, default=True)

    user = relationship("User", back_populates="routines")

    exercises = relationship(
        "RoutineExercise",
        back_populates="routine",
        cascade="all, delete-orphan"
    )


