import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.sales import models, schemas
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
        "role": "Vendedor"
    }
    response = client.post(
        "/users/",
        json=fake_user,
    )
    assert response.status_code == 200
    fake_user.update(response.json())
    return fake_user

@pytest.fixture(scope="module")
def token(test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_sale(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == fake_sale["product_id"]
    assert "id" in data

def test_read_sale(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    create_response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    sale_id = create_response.json()["id"]

    response = client.get(
        f"/sales/{sale_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == fake_sale["product_id"]

def test_read_sales(test_db, token):
    # Crear una venta para asegurarnos de que hay datos
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get(
        "/sales/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_sale(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    create_response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    sale_id = create_response.json()["id"]

    updated_sale = {
        "product_id": 2,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    response = client.put(
        f"/sales/{sale_id}",
        json=updated_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == updated_sale["product_id"]

def test_delete_sale(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    create_response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    sale_id = create_response.json()["id"]

    response = client.delete(
        f"/sales/{sale_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == fake_sale["product_id"]

    response = client.get(
        f"/sales/{sale_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_create_sale_unauthorized(test_db):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    response = client.post(
        "/sales/",
        json=fake_sale
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_sale_unauthorized(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    create_response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    sale_id = create_response.json()["id"]

    updated_sale = {
        "product_id": 2,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }

    # Simulate unauthorized user by not sending token
    response = client.put(
        f"/sales/{sale_id}",
        json=updated_sale
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_sale_unauthorized(test_db, token):
    fake_sale = {
        "product_id": 1,
        "price": faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    }
    create_response = client.post(
        "/sales/",
        json=fake_sale,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    sale_id = create_response.json()["id"]

    # Simulate unauthorized user by not sending token
    response = client.delete(
        f"/sales/{sale_id}"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
