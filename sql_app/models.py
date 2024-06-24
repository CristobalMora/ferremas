from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from Ferremas.sql_app.database import Base

class Boleta(Base):
    __tablename__ = "boletas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    transaction_id = Column(String, unique=True)
    amount = Column(Float)
    user = relationship("User", back_populates="boletas")
    items = relationship("CartItem", back_populates="boleta")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    cart_items = relationship("CartItem", back_populates="owner")
    boletas = relationship("Boleta", back_populates="user")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer)
    boleta_id = Column(Integer, ForeignKey("boletas.id"))

    owner = relationship("User", back_populates="cart_items")
    product = relationship("Product")
    boleta = relationship("Boleta", back_populates="items")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
