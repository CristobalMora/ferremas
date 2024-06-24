from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.sales import schemas, service
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Sale)
def create_sale(
    sale: schemas.SaleCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to add sale items"
        )
    return service.create_sale(db, sale)

@router.get("/", response_model=list[schemas.Sale])
def read_sales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return service.get_sales(db, skip, limit)
