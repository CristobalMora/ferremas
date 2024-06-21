from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter()

def verify_client_role(user: models.User):
    if user.role != "cliente":
        raise HTTPException(status_code=403, detail="Operation not permitted")

@router.post("/", response_model=schemas.CartItemResponse, tags=["Cart"])
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_cart_item = crud.add_to_cart(db=db, cart_item=cart_item, user_id=current_user.id)
    db_cart_item.product = product  # Asignar el producto cargado
    return db_cart_item

@router.delete("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    db_cart_item = crud.remove_from_cart(db=db, cart_item_id=cart_item_id, user_id=current_user.id)
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db_cart_item.product = db.query(models.Product).filter(models.Product.id == db_cart_item.product_id).first()
    return db_cart_item

@router.get("/", response_model=List[schemas.CartItemResponse], tags=["Cart"])
def view_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    db_cart_items = crud.get_cart_items(db=db, user_id=current_user.id)
    for item in db_cart_items:
        item.product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if item.product is None:
            item.product = None  # Si no se encuentra el producto, se asigna None
    return db_cart_items

@router.get("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def read_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    db_cart_item = crud.get_cart_item(db=db, cart_item_id=cart_item_id, user_id=current_user.id)
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db_cart_item.product = db.query(models.Product).filter(models.Product.id == db_cart_item.product_id).first()
    return db_cart_item

@router.put("/{cart_item_id}", response_model=schemas.CartItemResponse, tags=["Cart"])
def update_cart_item(cart_item_id: int, cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    db_cart_item = crud.update_cart_item(db=db, cart_item_id=cart_item_id, cart_item=cart_item, user_id=current_user.id)
    db_cart_item.product = db.query(models.Product).filter(models.Product.id == db_cart_item.product_id).first()
    return db_cart_item
