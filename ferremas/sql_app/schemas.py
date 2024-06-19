from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: str
    role: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True  # Actualiza a ConfigDict si es necesario en Pydantic V2

class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True  # Actualiza a ConfigDict si es necesario en Pydantic V2

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse

    class Config:
        orm_mode = True  # Actualiza a ConfigDict si es necesario en Pydantic V2

class Token(BaseModel):
    access_token: str
    token_type: str
