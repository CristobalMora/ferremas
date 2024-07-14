from sqlalchemy import Column, Integer, String
from database import Base

class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    direccion = Column(String)
    telefono = Column(String)
