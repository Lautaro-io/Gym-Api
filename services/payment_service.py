from fastapi import HTTPException
from sqlalchemy.sql.functions import user

from models import Payment
from repositories.payment_repository import PaymentRepository
from repositories.user_repository import UserRepository
from schemas.payment_schema import PaymentCreate
from datetime import datetime, timezone


class PaymentService:

    def __init__(self, payment_repository: PaymentRepository, user_repository: UserRepository):
        self.payment_repository = payment_repository
        self.user_repository = user_repository

    def get_payment(self, payment_id : int ) -> Payment:
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    def get_all_payments(self) -> list[Payment]:
        return self.payment_repository.get_all_payments()

    def get_payment_by_user(self, user_id: int) -> list[Payment]:
        user= self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.payment_repository.get_by_user(user_id)

    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        user = self.user_repository.get_by_id(payment_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        payment = Payment(**payment_data.model_dump())
        return self.payment_repository.create_payment(payment)

    def get_membership_status(self, user_id : int) ->dict:
        user =self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        last = self.payment_repository.get_last_by_user(user_id)
        if not last:
            return{"vigente": False, "expiration_date": None, "dias_restantes": None}

        exp = last.expiration_date
        if exp.tinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        return{ "vigente": exp >= now, "expiration_date": exp, "dias_restantes": (exp - now).days}
