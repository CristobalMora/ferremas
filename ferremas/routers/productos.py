from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db

router = APIRouter()

@router.get("/{product_id}", response_model=schemas.ProductCreate, tags=["Product"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
