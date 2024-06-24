from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    description = Column(String)
    quantity = Column(Integer)
    
    sale = relationship("Sale", uselist=False, back_populates="product")
