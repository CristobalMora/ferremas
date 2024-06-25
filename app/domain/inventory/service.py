from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.user.models import User
from app.domain.inventory import models, schemas, repository
from database import get_db

def get_inventory_item(db: Session, item_id: int):
    db_item = repository.get_inventory_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_item

def get_inventory_items(db: Session, skip: int = 0, limit: int = 10):
    return repository.get_inventory_items(db, skip, limit)

def create_inventory_item(db: Session, item: schemas.InventoryCreate, current_user: User):
    if current_user.role != "Bodega":
        raise HTTPException(status_code=403, detail="Not authorized to add inventory items")
    return repository.create_inventory_item(db, item)

def update_inventory_item(db: Session, item_id: int, item_update: schemas.InventoryCreate, current_user: User):
    if current_user.role != "Bodega":
        raise HTTPException(status_code=403, detail="Not authorized to update inventory items")
    db_item = repository.get_inventory_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return repository.update_inventory_item(db, db_item, item_update)

def delete_inventory_item(db: Session, item_id: int, quantity: int, current_user: User):
    if current_user.role != "Bodega":
        raise HTTPException(status_code=403, detail="Not authorized to delete inventory items")
    
    db_item = repository.get_inventory_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    if db_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Cannot delete more items than are available in inventory")
    
    db_item.quantity -= quantity
    
    if db_item.quantity == 0:
        repository.delete_inventory_item(db, db_item)
    else:
        db.commit()
        db.refresh(db_item)
    
    return db_item
