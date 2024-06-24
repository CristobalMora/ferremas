from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.inventory import models, schemas, service
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Inventory)
def create_inventory_item(
    item: schemas.InventoryCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Bodega":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to add inventory items"
        )
    return service.create_inventory_item(db, item, current_user)

@router.get("/{item_id}", response_model=schemas.Inventory)
def read_inventory_item(item_id: int, db: Session = Depends(get_db)):
    return service.get_inventory_item(db, item_id)

@router.get("/", response_model=list[schemas.Inventory])
def read_inventory_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return service.get_inventory_items(db, skip, limit)

@router.put("/{item_id}", response_model=schemas.Inventory)
def update_inventory_item(
    item_id: int, 
    item_update: schemas.InventoryCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Bodega":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update inventory items"
        )
    return service.update_inventory_item(db, item_id, item_update, current_user)

@router.delete("/{item_id}", response_model=schemas.Inventory)
def delete_inventory_item(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Bodega":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete inventory items"
        )
    return service.delete_inventory_item(db, item_id, current_user)
