from pydantic import BaseModel, Field
from datetime import datetime
from models.enums import MetodoPagoEnum

class PaymentCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    payment_method: MetodoPagoEnum
    expiration_date: datetime

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    payment_method: MetodoPagoEnum
    payment_date: datetime
    expiration_date: datetime

    class Config:
        from_attributes = True