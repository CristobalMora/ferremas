import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.inventory import models, schemas
from app.domain.user.models import User
from database import Base, get_db
from faker import Faker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
faker = Faker()

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user():
    fake_user = {
        "nombre": faker.name(),
        "correo": faker.email(),
        "password": faker.password(),
        "role": "Bodega"
    }
    response = client.post(
        "/users/",
        json=fake_user,
    )
    assert response.status_code == 200
    fake_user.update(response.json())  # Actualiza fake_user con la respuesta incluyendo el ID
    return fake_user

@pytest.fixture(scope="module")
def token(test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_inventory_item(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == fake_item["product_name"]
    assert "id" in data

def test_read_inventory_item(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    create_response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    response = client.get(
        f"/inventory/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == fake_item["product_name"]

def test_read_inventory_items(test_db, token):
    response = client.get(
        "/inventory/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_inventory_item(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    create_response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    updated_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    response = client.put(
        f"/inventory/{item_id}",
        json=updated_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == updated_item["product_name"]

def test_delete_inventory_item(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    create_response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    response = client.delete(
        f"/inventory/{item_id}/{fake_item['quantity']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == fake_item["product_name"]

    response = client.get(
        f"/inventory/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_create_inventory_item_unauthorized(test_db):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    response = client.post(
        "/inventory/",
        json=fake_item
    )
    assert response.status_code == 401  # Cambiado de 403 a 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_inventory_item_unauthorized(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    create_response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    updated_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }

    # Simulate unauthorized user by not sending token
    response = client.put(
        f"/inventory/{item_id}",
        json=updated_item
    )
    assert response.status_code == 401  # Cambiado de 403 a 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_inventory_item_unauthorized(test_db, token):
    fake_item = {
        "product_name": faker.word(),
        "description": faker.text(),
        "quantity": faker.random_int(min=1, max=100)
    }
    create_response = client.post(
        "/inventory/",
        json=fake_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    # Simulate unauthorized user by not sending token
    response = client.delete(
        f"/inventory/{item_id}/{fake_item['quantity']}"
    )
    assert response.status_code == 401  # Cambiado de 403 a 401
    assert response.json()["detail"] == "Not authenticated"
