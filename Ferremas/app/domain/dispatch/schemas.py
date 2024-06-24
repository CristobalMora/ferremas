from pydantic import BaseModel, EmailStr

class DispatchBase(BaseModel):
    address: str
    username: str
    email: EmailStr
    phone: str | None = None

class DispatchCreate(DispatchBase):
    pass

class Dispatch(DispatchBase):
    id: int
    total_cost: int

    class Config:
        from_attributes = True
