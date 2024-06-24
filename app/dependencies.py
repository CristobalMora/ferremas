from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from database import SessionLocal
from app.domain.user.models import User
from app.domain.user.repository import get_user_by_id
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Suponiendo que estás obteniendo el user_id del token
def get_user_id(token: str = Depends(oauth2_scheme)) -> int:
    # Aquí deberías decodificar el token y extraer el user_id
    # Este es un ejemplo simple, debes ajustar esto según tu lógica de autenticación
    user_id = decode_token(token)  # Necesitas implementar decode_token
    return user_id

def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
