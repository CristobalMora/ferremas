from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.CartItemResponse, tags=["Cart"])
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.add_to_cart(db=db, cart_item=cart_item, user_id=current_user.id)

@router.delete("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.remove_from_cart(db=db, cart_item_id=cart_item_id, user_id=current_user.id)

@router.get("/", response_model=List[schemas.CartItemResponse], tags=["Cart"])
def view_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_cart_items(db=db, user_id=int(current_user.id))

@router.get("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def read_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_cart_item = crud.get_cart_item(db=db, cart_item_id=cart_item_id, user_id=current_user.id)
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return db_cart_item

@router.put("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def update_cart_item(cart_item_id: int, cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.update_cart_item(db=db, cart_item_id=cart_item_id, cart_item=cart_item, user_id=current_user.id)
