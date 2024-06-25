from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.payment import service as payment_service, schemas as payment_schemas
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=payment_schemas.PaymentResponse)
def create_payment(
    payment: payment_schemas.PaymentCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to make a payment"
        )
    return payment_service.create_payment(db, payment, current_user)

@router.get("/{payment_id}", response_model=payment_schemas.PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    payment = payment_service.get_payment(db, payment_id)
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment not found"
        )
    return payment

@router.get("/", response_model=list[payment_schemas.PaymentResponse])
def list_payments(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to view payments"
        )
    return payment_service.list_payments(db, current_user)
