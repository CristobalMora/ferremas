from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)  # Asegúrate de que Float esté correctamente importado
    quantity = Column(Integer)
    
    sale = relationship("Sale", uselist=False, back_populates="product")
