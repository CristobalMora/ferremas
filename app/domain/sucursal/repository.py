from sqlalchemy.orm import Session
from app.domain.sucursal import models, schemas

def create_sucursal(db: Session, sucursal: schemas.SucursalCreate):
    db_sucursal = models.Sucursal(**sucursal.model_dump())
    db.add(db_sucursal)
    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal

def get_sucursal(db: Session, sucursal_id: int):
    return db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()

def get_sucursales(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Sucursal).offset(skip).limit(limit).all()

def update_sucursal(db: Session, db_sucursal: models.Sucursal, sucursal_update: schemas.SucursalCreate):
    for key, value in sucursal_update.model_dump().items():
        setattr(db_sucursal, key, value)
    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal

def delete_sucursal(db: Session, db_sucursal: models.Sucursal):
    db.delete(db_sucursal)
    db.commit()
