from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.user import repository, schemas
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_email(db, email=user.correo)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repository.create_user(db, user)
