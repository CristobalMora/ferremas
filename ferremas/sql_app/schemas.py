from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItem(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
