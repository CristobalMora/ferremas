import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # Asegúrate de que 'main.py' está en el directorio raíz
from Ferremas.sql_app.database import Base
from Ferremas.sql_app.dependencies import get_db

# Asegúrate de que el directorio raíz está en el sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Configuración de la base de datos para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override para usar la base de datos de pruebas
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Configuración de datos iniciales para pruebas
def setup_module(module):
    db = TestingSessionLocal()
    user = models.User(username="testuser", email="testuser@example.com", hashed_password="password", role="cliente")
    product = models.Product(name="Test Product", price=10.0)
    db.add(user)
    db.add(product)
    db.commit()
    db.refresh(user)
    db.refresh(product)
    module.user_id = user.id
    module.product_id = product.id

def teardown_module(module):
    db = TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
