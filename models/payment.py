from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base
from models.enums import MetodoPagoEnum


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(MetodoPagoEnum), nullable=False)

    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    expiration_date = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="payments")