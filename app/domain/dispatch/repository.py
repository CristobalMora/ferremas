from sqlalchemy.orm import Session
from . import models, schemas

def create_dispatch(db: Session, dispatch: schemas.DispatchCreate, user_id: int, total_cost: int):
    db_dispatch = models.Dispatch(**dispatch.model_dump(), user_id=user_id, total_cost=total_cost)
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch
