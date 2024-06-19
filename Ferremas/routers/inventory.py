from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.ProductCreate, tags=["Inventory"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "bodega":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.create_product(db=db, product=product)

@router.put("/{product_id}", response_model=schemas.ProductCreate, tags=["Inventory"])
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "bodega":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.update_product(db=db, product_id=product_id, product=product)

@router.get("/", response_model=List[schemas.ProductCreate], tags=["Inventory"])
def read_inventory(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "bodega" and str(current_user.role) != "vendedor":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    products = crud.get_products(db, skip=skip, limit=limit)
    return products
