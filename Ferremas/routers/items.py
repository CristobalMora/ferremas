from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.ProductCreate], tags=["Items"])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = crud.get_products(db, skip=skip, limit=limit)
    return items
