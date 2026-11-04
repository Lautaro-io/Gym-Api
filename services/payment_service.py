from fastapi import HTTPException
from models import Payment
from repositories.payment_repository import PaymentRepository
from repositories.user_repository import UserRepository
from schemas.payment_schema import MembershipStatusResponse, PaymentCreate
from datetime import datetime, timezone
from math import ceil


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
        if self._as_utc(payment_data.expiration_date) <= datetime.now(timezone.utc):
            raise HTTPException(status_code=422, detail="expiration_date must be in the future")
        payment = Payment(**payment_data.model_dump())
        return self.payment_repository.create_payment(payment)

    def get_membership_status(self, user_id : int) -> MembershipStatusResponse:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        current_payment = self.payment_repository.get_max_expiration_by_user(user_id)
        if not current_payment:
            return MembershipStatusResponse(vigente=False, expiration_date=None, dias_restantes=0)
        expiration = self._as_utc(current_payment.expiration_date)
        now = datetime.now(timezone.utc)
        remaining_seconds = (expiration - now).total_seconds()
        return MembershipStatusResponse(
            vigente=remaining_seconds > 0,
            expiration_date=expiration,
            dias_restantes=max(0, ceil(remaining_seconds / 86400)),
        )

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
