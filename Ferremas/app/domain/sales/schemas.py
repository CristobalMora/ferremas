from pydantic import BaseModel

class SaleBase(BaseModel):
    product_id: int
    price: float

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int

    class Config:
        from_attributes = True
