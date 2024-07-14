import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.cart import models, schemas
from app.domain.user.models import User
from app.domain.sales.models import Sale
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
        "role": "Cliente"  
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

@pytest.fixture(scope="module")
def test_sale(test_db):
    db = TestingSessionLocal()
    fake_sale = Sale(
        product_id=1,
        price=faker.pyfloat(min_value=1, max_value=100, right_digits=2)
    )
    db.add(fake_sale)
    db.commit()
    db.refresh(fake_sale)
    db.close()
    return fake_sale

def test_add_to_cart(test_db, token, test_sale):
    fake_cart_item = {
        "sale_id": test_sale.id,
        "quantity": faker.random_int(min=1, max=10)
    }
    response = client.post(
        "/cart/",
        json=fake_cart_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["sale_id"] == fake_cart_item["sale_id"]
    assert data["quantity"] == fake_cart_item["quantity"]
    assert "id" in data

def test_get_cart_items(test_db, token):
    
    fake_cart_item = {
        "sale_id": 1,
        "quantity": faker.random_int(min=1, max=10)
    }
    client.post(
        "/cart/",
        json=fake_cart_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    response = client.get(
        "/cart/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) > 0

def test_remove_from_cart(test_db, token, test_sale):
    fake_cart_item = {
        "sale_id": test_sale.id,
        "quantity": faker.random_int(min=1, max=10)
    }
    create_response = client.post(
        "/cart/",
        json=fake_cart_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200, create_response.text
    item_id = create_response.json()["id"]

    response = client.delete(
        f"/cart/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["sale_id"] == fake_cart_item["sale_id"]
    assert data["quantity"] == fake_cart_item["quantity"]

def test_add_to_cart_unauthorized(test_db, test_sale):
    fake_cart_item = {
        "sale_id": test_sale.id,
        "quantity": faker.random_int(min=1, max=10)
    }
    response = client.post(
        "/cart/",
        json=fake_cart_item
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_get_cart_items_unauthorized(test_db):
    response = client.get("/cart/")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_remove_from_cart_unauthorized(test_db, test_sale, token):
    fake_cart_item = {
        "sale_id": test_sale.id,
        "quantity": faker.random_int(min=1, max=10)
    }
    create_response = client.post(
        "/cart/",
        json=fake_cart_item,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200, create_response.text
    item_id = create_response.json()["id"]

    response = client.delete(
        f"/cart/{item_id}"
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"
