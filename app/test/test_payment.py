import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.user import models as user_models
from app.domain.payment import models as payment_models
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

def test_create_payment(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}
    payment_data = {"amount": 10000}
    response = test_client.post(
        "/payments/",
        json=payment_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["amount"] == payment_data["amount"]
    assert data["status"] == "pending"

def test_get_payment(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}
    
    # Crear un pago primero
    payment_data = {"amount": 10000}
    response = test_client.post(
        "/payments/",
        json=payment_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    payment = response.json()

    # Obtener detalles del pago
    payment_id = payment["id"]
    response = test_client.get(
        f"/payments/{payment_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == payment_id
    assert data["amount"] == payment["amount"]
    assert data["status"] == payment["status"]
