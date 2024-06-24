from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class RoleEnum(enum.Enum):
    Bodega = "Bodega"
    Cliente = "Cliente"
    Administrador = "Administrador"
    Vendedor = "Vendedor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    correo = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    dispatches = relationship("Dispatch", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    payments = relationship("Payment", back_populates="user")
