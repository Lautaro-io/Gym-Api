from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.payment_repository import PaymentRepository
from repositories.user_repository import UserRepository
from schemas.payment_schema import PaymentCreate, PaymentResponse
from security.jwt_service import get_current_user
from security.permissions import require_admin
from services import payment_service
from services.payment_service import PaymentService

router = APIRouter(tags=["Payment"], prefix="/payment")


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, current_user: User = Depends(require_admin),
                   db: Session = Depends(get_db)) -> PaymentResponse:
    payment_service = PaymentService(PaymentRepository(db), UserRepository(db))
    return payment_service.create_payment(payment_data)

@router.get("", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
def get_all_payments(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    payments_service = PaymentService(PaymentRepository(db), UserRepository(db))
    return payments_service.get_all_payments()

@router.get("/me", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
def get_my_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payment_service = PaymentService(PaymentRepository(db), UserRepository(db))
    return payment_service.get_payment_by_user(current_user.id)

@router.get("/{id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def get_payment_by_id(id:int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    payment_service = PaymentService(PaymentRepository(db), UserRepository(db))
    return payment_service.get_payment(id)