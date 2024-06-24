from sqlalchemy.orm import Session
from . import models, schemas
from app.domain.sales.models import Sale

def get_cart_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.CartItem).offset(skip).limit(limit).all()

def create_cart_item(db: Session, cart_item: schemas.CartItemCreate):
    db_cart_item = models.CartItem(**cart_item.model_dump())
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def get_cart_item(db: Session, cart_item_id: int):
    return db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()

def get_cart_item_details(db: Session):
    return db.query(models.CartItem, Sale).join(Sale).all()
