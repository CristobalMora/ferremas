from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.cart import models as cart_models
from app.domain.sales import models as sales_models
from app.domain.inventory import models as inventory_models
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.get("/", response_model=dict)
def get_cart_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to view cart summary"
        )
    
    cart_items = db.query(cart_models.CartItem).filter(cart_models.CartItem.user_id == current_user.id).all()
    summary = []

    for item in cart_items:
        sale = db.query(sales_models.Sale).filter(sales_models.Sale.id == item.sale_id).first()
        inventory = db.query(inventory_models.Inventory).filter(inventory_models.Inventory.id == sale.product_id).first()
        
        summary.append({
            "product_name": inventory.product_name,
            "quantity": item.quantity,
            "price": sale.price,
            "total": item.quantity * sale.price
        })

    total_amount = sum(item["total"] for item in summary)
    
    return {"items": summary, "total_amount": total_amount}
