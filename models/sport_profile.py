from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class SportProfile(Base):
    __tablename__ = "sport_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    goal = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False)
    days_per_week = Column(Integer, nullable=False)
    session_duration = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)   
    injuries = Column(String(255), nullable=True)
    trainer_tracking = Column(Boolean, default=False)

    user = relationship("User", back_populates="sport_profiles")