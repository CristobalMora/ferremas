from sqlalchemy.orm import Session
from . import models, schemas

def get_sales(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Sale).offset(skip).limit(limit).all()

def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sale(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()

def update_sale(db: Session, sale_id: int, sale_update: schemas.SaleCreate):
    db_sale = get_sale(db, sale_id)
    db_sale.product_id = sale_update.product_id
    db_sale.price = sale_update.price
    db.commit()
    db.refresh(db_sale)
    return db_sale

def delete_sale(db: Session, sale_id: int):
    db_sale = get_sale(db, sale_id)
    db.delete(db_sale)
    db.commit()
    return db_sale
