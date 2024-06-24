from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter()

def verify_client_role(user: models.User):
    if user.role != "cliente":
        raise HTTPException(status_code=403, detail="Operation not permitted")

@router.get("/summary", response_model=schemas.CartSummaryResponse, tags=["Cart Summary"])
def cart_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    verify_client_role(current_user)
    db_cart_items = crud.get_cart_items(db=db, user_id=current_user.id)
    
    if not db_cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty")

    total_amount = 0
    cart_summary = []

    for item in db_cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            item_total = product.price * item.quantity
            total_amount += item_total
            cart_summary.append(schemas.CartItemSummary(
                product_name=product.name,
                quantity=item.quantity,
                price=product.price,
                item_total=item_total
            ))

    return schemas.CartSummaryResponse(
        total_amount=total_amount,
        items=cart_summary
    )
