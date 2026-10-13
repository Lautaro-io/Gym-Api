from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from db import Base
from models.enums import GrupoMuscularEnum


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    muscular_group = Column(Enum(GrupoMuscularEnum), nullable=False, default=GrupoMuscularEnum.PECHO)

    routines = relationship(
        "RoutineExercise",
        back_populates="exercise"
    )

