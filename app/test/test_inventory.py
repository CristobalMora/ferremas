import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.inventory import models as inventory_models, schemas as inventory_schemas
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
def bodega_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": "password123",  # Usamos una contraseña fija para facilitar la autenticación
        "role": "Bodega"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 200
    return user_data

@pytest.fixture(scope="module")
def bodega_token(test_client, bodega_user):
    response = test_client.post(
        "/token",
        data={"username": bodega_user["correo"], "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_create_inventory_item(test_client, bodega_token):
    headers = {"Authorization": f"Bearer {bodega_token}"}
    inventory_data = {
        "product_name": "Martillo",
        "description": "Para martillar",
        "quantity": 10
    }
    response = test_client.post(
        "/inventory/",
        json=inventory_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["product_name"] == inventory_data["product_name"]
    assert data["description"] == inventory_data["description"]
    assert data["quantity"] == inventory_data["quantity"]
    assert "id" in data

def test_read_inventory_item(test_client, bodega_token):
    headers = {"Authorization": f"Bearer {bodega_token}"}
    response = test_client.get("/inventory/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["product_name"] == "Martillo"
    assert data["description"] == "Para martillar"
    assert data["quantity"] == 10

def test_read_inventory_items(test_client, bodega_token):
    headers = {"Authorization": f"Bearer {bodega_token}"}
    response = test_client.get("/inventory/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) > 0

def test_update_inventory_item(test_client, bodega_token):
    headers = {"Authorization": f"Bearer {bodega_token}"}
    inventory_update_data = {
        "product_name": "Martillo",
        "description": "Para martillar cosas grandes",
        "quantity": 15
    }
    response = test_client.put("/inventory/1", json=inventory_update_data, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["product_name"] == inventory_update_data["product_name"]
    assert data["description"] == inventory_update_data["description"]
    assert data["quantity"] == inventory_update_data["quantity"]

def test_delete_inventory_item(test_client, bodega_token):
    headers = {"Authorization": f"Bearer {bodega_token}"}
    response = test_client.delete("/inventory/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["product_name"] == "Martillo"
    assert data["description"] == "Para martillar"
    assert data["quantity"] == 15
