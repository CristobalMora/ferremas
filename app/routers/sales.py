from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.sales import schemas, service, models
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Sale)
def create_sale(
    sale: schemas.SaleCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    return service.create_sale(db, sale, current_user)

@router.get("/", response_model=list[schemas.Sale])
def read_sales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_sales(db, skip, limit)

@router.get("/{sale_id}", response_model=schemas.Sale)
def read_sale(sale_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_sale(db, sale_id)

@router.put("/{sale_id}", response_model=schemas.Sale)
def update_sale(
    sale_id: int, 
    sale: schemas.SaleCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    return service.update_sale(db, sale_id, sale, current_user)

@router.delete("/{sale_id}", response_model=schemas.Sale)
def delete_sale(sale_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.delete_sale(db, sale_id, current_user)
