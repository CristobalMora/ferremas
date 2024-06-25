from pydantic import BaseModel, Field
from typing import Annotated

class CartItemBase(BaseModel):
    sale_id: int
    quantity: Annotated[int, Field(gt=0)]  # Esta línea asegura que la cantidad sea mayor que 0

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
