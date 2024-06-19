from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Ferremas.sql_app import models
from Ferremas.sql_app.dependencies import get_db, get_current_user
import uuid

router = APIRouter()

@router.post("/", response_model=dict, tags=["Payment Service"])
def pay(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if str(current_user.role) != "cliente":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    buy_order = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    return_url = "https://yourdomain.com/payment/return"
    
    response = {
        "url": "https://webpay.mock/request",
        "token": "mock_token",
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": total_amount,
        "return_url": return_url,
    }
    
    return response
