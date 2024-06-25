from pydantic import BaseModel, Field

class SaleBase(BaseModel):
    product_id: int
    price: float = Field(gt=0, description="The price must be greater than zero.")

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int

    class Config:
        from_attributes = True