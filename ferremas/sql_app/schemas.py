from pydantic import BaseModel
from typing import Optional, List

# Product Schemas
class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Cart Item Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Cart Summary Schemas
class CartItemSummary(BaseModel):
    product_name: str
    quantity: int
    price: float
    item_total: float

class CartSummaryResponse(BaseModel):
    total_amount: float
    items: List[CartItemSummary]

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Boleta Schemas
class BoletaBase(BaseModel):
    user_id: int
    transaction_id: str
    amount: float

class BoletaCreate(BoletaBase):
    pass

class BoletaResponse(BoletaBase):
    id: int

    class Config:
        from_attributes = True
