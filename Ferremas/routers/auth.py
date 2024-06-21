from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from Ferremas.sql_app import crud, schemas, models
from Ferremas.sql_app.dependencies import get_db

SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)  # Aquí 'username' es el correo electrónico
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})  # Usa 'email' en lugar de 'username'
    return {"access_token": access_token, "token_type": "bearer"}

def authenticate_user(db: Session, email: Optional[str], password: Optional[str]) -> Optional[models.User]:
    if email is None or password is None:
        return None
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not crud.verify_password(password, user.hashed_password):
        return None
    return user
