from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    Bodega = "Bodega"
    Cliente = "Cliente"
    Administrador = "Administrador"
    Vendedor = "Vendedor"

class UserBase(BaseModel):
    nombre: str = Field(..., json_schema_extra={"example": "Juan Perez"})
    correo: EmailStr = Field(..., json_schema_extra={"example": "juan@example.com"})
    role: RoleEnum = Field(..., json_schema_extra={"example": "Cliente"})

class UserCreate(UserBase):
    password: str = Field(..., json_schema_extra={"example": "password"})

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True  # Actualización para Pydantic v2
    }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
