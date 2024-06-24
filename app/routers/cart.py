from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.cart import schemas, service
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.CartItem)
def add_to_cart(
    cart_item: schemas.CartItemCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to add items to the cart"
        )
    return service.create_cart_item(db, cart_item, current_user.id)

@router.get("/", response_model=list[schemas.CartItem])
def get_cart_items(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to view cart items"
        )
    return service.get_cart_items(db, current_user.id)

@router.delete("/{item_id}", response_model=schemas.CartItem)
def remove_from_cart(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to remove items from the cart"
        )
    return service.delete_cart_item(db, item_id, current_user.id)
