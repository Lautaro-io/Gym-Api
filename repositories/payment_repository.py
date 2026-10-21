from sqlalchemy.orm import Session

from models import Payment


class PaymentRepository:
    def __init__(self , db : Session):
        self.db = db

    def create_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_all_payments(self) -> list[Payment]:
        return self.db.query(Payment).all()

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_by_user(self, user_id: int) -> list[Payment]:
        return self.db.query(Payment).filter(Payment.user_id == user_id).all()


