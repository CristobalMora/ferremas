from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int):
    db_dispatch = models.Dispatch(**dispatch.dict(), user_id=user_id, total_cost=3000)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch

def get_dispatch(db: Session, dispatch_id: int):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return db_dispatch

def update_dispatch(db: Session, dispatch_id: int, dispatch: schemas.DispatchCreate):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    for key, value in dispatch.dict().items():
        setattr(db_dispatch, key, value)
    db_dispatch.total_cost = db_dispatch.total_cost or 3000
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch

def delete_dispatch(db: Session, dispatch_id: int):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    db.delete(db_dispatch)
    db.commit()
    return db_dispatch

def list_dispatches(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Dispatch).filter(models.Dispatch.user_id == user_id).offset(skip).limit(limit).all()
