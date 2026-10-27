from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import MetodoPagoEnum


class PaymentCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    payment_method: MetodoPagoEnum
    expiration_date: datetime

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    payment_method: MetodoPagoEnum
    payment_date: datetime
    expiration_date: datetime

    model_config = ConfigDict(from_attributes=True)