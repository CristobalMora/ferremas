from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    user = relationship("User", back_populates="cart_items")
    sale = relationship("Sale")