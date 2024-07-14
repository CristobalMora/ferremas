from sqlalchemy.orm import Session
from app.domain.sucursal import repository, schemas
from app.domain.user.models import User
from . import models, schemas, repository
from fastapi import HTTPException, status


def create_sucursal(db: Session, sucursal: schemas.SucursalCreate, current_user: User):
    if current_user.role != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return repository.create_sucursal(db, sucursal)

def get_sucursal(db: Session, sucursal_id: int):
    return repository.get_sucursal(db, sucursal_id)

def get_sucursales(db: Session, skip: int = 0, limit: int = 10):
    return repository.get_sucursales(db, skip, limit)

def update_sucursal(db: Session, sucursal_id: int, sucursal: schemas.SucursalCreate, current_user: User):
    if current_user.role != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    db_sucursal = repository.get_sucursal(db, sucursal_id)
    if not db_sucursal:
        raise HTTPException(status_code=404, detail="Sucursal not found")
    return repository.update_sucursal(db, db_sucursal, sucursal)

def delete_sucursal(db: Session, sucursal_id: int, current_user: User):
    if current_user.role != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    db_sucursal = repository.get_sucursal(db, sucursal_id)
    if not db_sucursal:
        raise HTTPException(status_code=404, detail="Sucursal not found")
    return repository.delete_sucursal(db, db_sucursal)
