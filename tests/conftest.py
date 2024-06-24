import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from main import app
from Ferremas.sql_app.dependencies import get_db
import Ferremas.sql_app.models as models
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"  # Asegúrate de que esto coincida con tu configuración real
ALGORITHM = "HS256"

def create_fake_token(user_id: int, username: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": str(user_id), "username": username, "exp": expiration}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Asegúrate de que el directorio raíz está en el sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración de la base de datos para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@pytest.fixture(scope='module')
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='module')
def test_client():
    return TestClient(app)

@pytest.fixture(scope='function')
def fake_data(test_db):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Pobla la base de datos con datos ficticios
    user = models.User(username="testuser", email="testuser@example.com", hashed_password="password", role="cliente")
    product = models.Product(name="Test Product", price=10.0)
    test_db.add(user)
    test_db.add(product)
    test_db.commit()
    test_db.refresh(user)
    test_db.refresh(product)
    return {'user_id': user.id, 'product_id': product.id}
