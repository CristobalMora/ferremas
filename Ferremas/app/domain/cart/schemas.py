from pydantic import BaseModel

class CartItemBase(BaseModel):
    sale_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
