import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from Ferremas.sql_app import models, schemas
from typing import List


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar si el nuevo correo electrónico ya está en uso
    if user.email and user.email != db_user.email:
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.dict(exclude_unset=True)
    if user.password:
        user_dict["hashed_password"] = pwd_context.hash(user.password)

    for key, value in user_dict.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

## carrito de compras 

def add_to_cart(db: Session, cart_item: schemas.CartItemCreate, user_id: int) -> models.CartItem:
    db_cart_item = models.CartItem(**cart_item.model_dump(), user_id=user_id)
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def remove_from_cart(db: Session, cart_item_id: int, user_id: int) -> models.CartItem:
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item

def get_cart_items(db: Session, user_id: int) -> List[models.CartItem]:
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def get_cart_item(db: Session, cart_item_id: int, user_id: int) -> models.CartItem:
    return db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()

def update_cart_item(db: Session, cart_item_id: int, cart_item: schemas.CartItemCreate, user_id: int) -> models.CartItem:
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    for key, value in cart_item.model_dump().items():
        setattr(db_cart_item, key, value)
    db.commit()
    return db_cart_item

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 10) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product: schemas.ProductCreate) -> models.Product:
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_all_sales(db: Session):
    return db.query(models.CartItem).all()

def create_boleta(db: Session, boleta: schemas.BoletaCreate):
    db_boleta = models.Boleta(**boleta.model_dump())
    db.add(db_boleta)
    db.commit()
    db.refresh(db_boleta)
    return db_boleta

def get_boleta(db: Session, boleta_id: int):
    return db.query(models.Boleta).filter(models.Boleta.id == boleta_id).first()

def get_boletas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Boleta).offset(skip).limit(skip).all()
