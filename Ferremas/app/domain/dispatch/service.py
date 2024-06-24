from sqlalchemy.orm import Session
from . import repository, schemas

def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int):
    total_cost = 3000  # Coste extra fijo
    return repository.create_dispatch(db, dispatch, user_id, total_cost)
