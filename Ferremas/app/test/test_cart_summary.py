import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.user import models as user_models
from app.domain.cart import models as cart_models
from app.domain.sales import models as sales_models
from database import Base, get_db
from main import app
from faker import Faker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia sobreescrita para pruebas
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

fake = Faker()

@pytest.fixture(scope="module")
def cliente_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": "password123",
        "role": "Cliente"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 200
    return user_data

@pytest.fixture(scope="module")
def cliente_token(test_client, cliente_user):
    response = test_client.post(
        "/token",
        data={"username": cliente_user["correo"], "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_get_cart_summary(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}
    response = test_client.get(
        "/cart_summary/",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total_amount" in data
