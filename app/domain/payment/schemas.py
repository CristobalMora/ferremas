from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    amount: int

class PaymentResponse(BaseModel):
    id: int
    amount: int
    status: str

    class Config:
        from_attributes = True
