from pydantic import BaseModel

class SucursalBase(BaseModel):
    nombre: str
    direccion: str
    telefono: str

class SucursalCreate(SucursalBase):
    pass

class Sucursal(SucursalBase):
    id: int

    class Config:
        orm_mode = True

class Message(BaseModel):
    detail: str