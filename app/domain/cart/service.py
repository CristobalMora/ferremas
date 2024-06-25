from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, status

def create_cart_item(db: Session, cart_item: schemas.CartItemCreate, user_id: int):
    db_cart_item = models.CartItem(**cart_item.model_dump(), user_id=user_id)
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def get_cart_items(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def delete_cart_item(db: Session, item_id: int, user_id: int):
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.user_id == user_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
        return db_cart_item
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
