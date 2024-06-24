from pydantic import BaseModel, Field

class InventoryBase(BaseModel):
    product_name: str = Field(..., json_schema_extra={"example": "martillo"})
    description: str = Field(..., json_schema_extra={"example": "para martillar"})
    quantity: int = Field(..., json_schema_extra={"example": 10})

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int

    model_config = {
        "from_attributes": True
    }
