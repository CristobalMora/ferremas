from sqlalchemy.orm import Session
from . import models, schemas

def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sales(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Sale).offset(skip).limit(limit).all()
