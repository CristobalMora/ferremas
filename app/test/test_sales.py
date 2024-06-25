import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.sales import schemas as sales_schemas
from app.domain.user import models as user_models
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
def vendedor_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": "password123",
        "role": "Vendedor"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 200
    return user_data

@pytest.fixture(scope="module")
def vendedor_token(test_client, vendedor_user):
    response = test_client.post(
        "/token",
        data={"username": vendedor_user["correo"], "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

@pytest.fixture(scope="module")
def created_sale(test_client, vendedor_token):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    sale_data = {
        "product_id": 1,
        "price": 19.99
    }
    response = test_client.post(
        "/sales/",
        json=sale_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()

def test_create_sale(test_client, vendedor_token):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    sale_data = {
        "product_id": 1,
        "price": 19.99
    }
    response = test_client.post(
        "/sales/",
        json=sale_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["product_id"] == sale_data["product_id"]
    assert data["price"] == sale_data["price"]
    assert "id" in data

def test_create_sale_invalid_price(test_client, vendedor_token):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    sale_data = {
        "product_id": 1,
        "price": -10.0  # Precio no válido
    }
    response = test_client.post(
        "/sales/",
        json=sale_data,
        headers=headers
    )
    assert response.status_code == 422, response.text

def test_read_sales(test_client, vendedor_token):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    response = test_client.get("/sales/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) > 0

def test_read_sale(test_client, vendedor_token, created_sale):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    response = test_client.get(f"/sales/{created_sale['id']}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == created_sale["id"]

def test_update_sale(test_client, vendedor_token, created_sale):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    sale_update_data = {
        "product_id": 1,
        "price": 29.99
    }
    response = test_client.put(f"/sales/{created_sale['id']}", json=sale_update_data, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["price"] == sale_update_data["price"]

def test_update_sale_invalid_price(test_client, vendedor_token, created_sale):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    sale_update_data = {
        "product_id": 1,
        "price": -29.99  # Precio no válido
    }
    response = test_client.put(f"/sales/{created_sale['id']}", json=sale_update_data, headers=headers)
    assert response.status_code == 422, response.text

def test_delete_sale(test_client, vendedor_token, created_sale):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    response = test_client.delete(f"/sales/{created_sale['id']}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == created_sale["id"]

def test_delete_nonexistent_sale(test_client, vendedor_token):
    headers = {"Authorization": f"Bearer {vendedor_token}"}
    response = test_client.delete("/sales/999", headers=headers)  # ID no existente
    assert response.status_code == 404, response.text
