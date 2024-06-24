from sqlalchemy.orm import Session
from . import repository, schemas

def create_sale(db: Session, sale: schemas.SaleCreate):
    return repository.create_sale(db, sale)

def get_sales(db: Session, skip: int = 0, limit: int = 10):
    return repository.get_sales(db, skip, limit)
