from sqlalchemy.orm import Session
from . import models, schemas

def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int, total_cost: int):
    db_dispatch = models.Dispatch(**dispatch.dict(), user_id=user_id, total_cost=total_cost)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch

def get_dispatch(db: Session, dispatch_id: int):
    return db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()

def update_dispatch(db: Session, dispatch_id: int, dispatch: schemas.DispatchCreate):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch:
        for key, value in dispatch.dict().items():
            setattr(db_dispatch, key, value)
        db.commit()
        db.refresh(db_dispatch)
    return db_dispatch

def delete_dispatch(db: Session, dispatch_id: int):
    db_dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if db_dispatch:
        db.delete(db_dispatch)
        db.commit()
    return db_dispatch

def list_dispatches(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Dispatch).filter(models.Dispatch.user_id == user_id).offset(skip).limit(limit).all()
