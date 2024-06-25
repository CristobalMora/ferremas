from sqlalchemy.orm import Session
from . import repository, schemas

def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int):
    total_cost = 3000  # Coste extra fijo
    return repository.create_dispatch(db, dispatch, user_id, total_cost)

def get_dispatch(db: Session, dispatch_id: int):
    return repository.get_dispatch(db, dispatch_id)

def update_dispatch(db: Session, dispatch_id: int, dispatch: schemas.DispatchCreate):
    return repository.update_dispatch(db, dispatch_id, dispatch)

def delete_dispatch(db: Session, dispatch_id: int):
    return repository.delete_dispatch(db, dispatch_id)

def list_dispatches(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return repository.list_dispatches(db, user_id, skip=skip, limit=limit)
