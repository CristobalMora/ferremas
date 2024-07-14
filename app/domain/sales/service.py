from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models, schemas, repository

def create_sale(db: Session, sale: schemas.SaleCreate, current_user):
    if current_user.role != "Vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to add sale items"
        )
    return repository.create_sale(db, sale)

def get_sales(db: Session, skip: int = 0, limit: int = 10):
    return repository.get_sales(db, skip, limit)

def get_sale(db: Session, sale_id: int):
    db_sale = repository.get_sale(db, sale_id)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale

def update_sale(db: Session, sale_id: int, sale_update: schemas.SaleCreate, current_user):
    db_sale = repository.get_sale(db, sale_id)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if current_user.role != "Vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update sale items"
        )
    db_sale.product_id = sale_update.product_id
    db_sale.price = sale_update.price
    db.commit()
    db.refresh(db_sale)
    return db_sale

def delete_sale(db: Session, sale_id: int, current_user):
    db_sale = repository.get_sale(db, sale_id)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if current_user.role != "Vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete sale items"
        )
    repository.delete_sale(db, sale_id)
    db.commit()
    return db_sale
