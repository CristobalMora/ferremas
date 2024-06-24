from sqlalchemy.orm import Session
from . import models, schemas

def get_inventory_item(db: Session, item_id: int):
    return db.query(models.Inventory).filter(models.Inventory.id == item_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Inventory).offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    db_item = models.Inventory(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_inventory_item(db: Session, db_item: models.Inventory, item_update: schemas.InventoryCreate):
    db_item.product_name = item_update.product_name
    db_item.description = item_update.description
    db_item.quantity = item_update.quantity
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_inventory_item(db: Session, db_item: models.Inventory):
    db.delete(db_item)
    db.commit()
