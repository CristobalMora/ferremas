from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.user import models, schemas, service, repository
from database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_email(db, user.correo)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = service.get_password_hash(user.password)
    db_user = models.User(
        nombre=user.nombre,
        correo=user.correo,
        hashed_password=hashed_password,
        role=user.role,
    )
    repository.create_user(db, db_user)
    return db_user

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(service.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = repository.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = repository.update_user(db, db_user, user)
    return updated_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    repository.delete_user(db, db_user)
    return db_user
