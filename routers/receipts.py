from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.CartItemResponse], tags=["Receipts"])
def read_receipts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "cliente":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.get_cart_items(db=db, user_id=current_user.id)
