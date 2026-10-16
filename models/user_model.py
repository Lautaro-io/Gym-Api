from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import Base
from models.enums import RolEnum, UserStateEnum


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, index=True, nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum(RolEnum), nullable=False, default=RolEnum.CLIENTE)
    state = Column(Enum(UserStateEnum), nullable=False, default=UserStateEnum.PENDIENTE_HABILITACION)
    register_date = Column(DateTime(timezone=True), server_default=func.now())

    routines = relationship("Routine", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    sport_profiles = relationship(
        "SportProfile", back_populates="user", cascade="all, delete-orphan"
    )
