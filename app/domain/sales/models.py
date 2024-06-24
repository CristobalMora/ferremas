from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory.id"))
    price = Column(Float, nullable=False)

    product = relationship("Inventory", back_populates="sale")
    cart_items = relationship("CartItem", back_populates="sale")
