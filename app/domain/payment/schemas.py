from pydantic import BaseModel

class PaymentCreate(BaseModel):
    amount: int

class PaymentResponse(BaseModel):
    id: int
    amount: int
    status: str

    class Config:
        from_attributes = True
