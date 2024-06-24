from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_current_user, get_db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.CartItemCreate], tags=["Sales"])
def view_sales(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "vendedor":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.get_all_sales(db=db)
