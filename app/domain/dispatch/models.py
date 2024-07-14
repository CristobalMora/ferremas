from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_cost = Column(Float, default=3000) 

    user = relationship("User", back_populates="dispatches")
