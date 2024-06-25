from sqlalchemy.orm import Session
from app.domain.payment.models import Payment
from app.domain.payment.schemas import PaymentCreate
from app.domain.user.models import User

def create_payment(db: Session, payment: PaymentCreate, user: User):
    db_payment = Payment(
        user_id=user.id,
        amount=payment.amount,
        status="pending"
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def list_payments(db: Session, user):
    return db.query(Payment).filter(Payment.user_id == user.id).all()
