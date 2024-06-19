import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from Ferremas.sql_app import models, schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)

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

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

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

def add_to_cart(db: Session, cart_item: schemas.CartItemCreate, user_id: int):
    db_cart_item = models.CartItem(product_id=cart_item.product_id, quantity=cart_item.quantity, user_id=user_id)
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def remove_from_cart(db: Session, cart_item_id: int, user_id: int):
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item

def get_cart_items(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def get_cart_item(db: Session, cart_item_id: int, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()

def update_cart_item(db: Session, cart_item_id: int, cart_item: schemas.CartItemCreate, user_id: int):
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id).first()
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    for key, value in cart_item.dict().items():
        setattr(db_cart_item, key, value)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product: schemas.ProductCreate):
    logging.info(f"Updating product with ID: {product_id}")
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        logging.error(f"Product with ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    logging.info(f"Product updated with ID: {product_id}")
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_all_sales(db: Session):
    return db.query(models.CartItem).all()
