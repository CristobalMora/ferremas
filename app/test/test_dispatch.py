import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.dispatch import models as dispatch_models, schemas as dispatch_schemas
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

def test_create_dispatch(test_db, token):
    fake_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    response = client.post(
        "/dispatch/",
        json=fake_dispatch,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["address"] == fake_dispatch["address"]
    assert data["username"] == fake_dispatch["username"]
    assert data["email"] == fake_dispatch["email"]
    assert data["phone"] == fake_dispatch["phone"]
    assert data["total_cost"] == fake_dispatch["total_cost"]
    assert "id" in data

def test_get_dispatch(test_db, token):
    fake_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    create_response = client.post(
        "/dispatch/",
        json=fake_dispatch,
        headers={"Authorization": f"Bearer {token}"}
    )
    dispatch_id = create_response.json()["id"]

    response = client.get(
        f"/dispatch/{dispatch_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["address"] == fake_dispatch["address"]
    assert data["username"] == fake_dispatch["username"]
    assert data["email"] == fake_dispatch["email"]
    assert data["phone"] == fake_dispatch["phone"]
    assert data["total_cost"] == fake_dispatch["total_cost"]

def test_list_dispatches(test_db, token):
    response = client.get(
        "/dispatch/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_update_dispatch(test_db, token):
    fake_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    create_response = client.post(
        "/dispatch/",
        json=fake_dispatch,
        headers={"Authorization": f"Bearer {token}"}
    )
    dispatch_id = create_response.json()["id"]

    updated_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    response = client.put(
        f"/dispatch/{dispatch_id}",
        json=updated_dispatch,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["address"] == updated_dispatch["address"]
    assert data["username"] == updated_dispatch["username"]
    assert data["email"] == updated_dispatch["email"]
    assert data["phone"] == updated_dispatch["phone"]
    assert data["total_cost"] == updated_dispatch["total_cost"]

def test_delete_dispatch(test_db, token):
    fake_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    create_response = client.post(
        "/dispatch/",
        json=fake_dispatch,
        headers={"Authorization": f"Bearer {token}"}
    )
    dispatch_id = create_response.json()["id"]

    response = client.delete(
        f"/dispatch/{dispatch_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["address"] == fake_dispatch["address"]
    assert data["username"] == fake_dispatch["username"]
    assert data["email"] == fake_dispatch["email"]
    assert data["phone"] == fake_dispatch["phone"]
    assert data["total_cost"] == fake_dispatch["total_cost"]

def test_create_dispatch_unauthorized(test_db):
    fake_dispatch = {
        "address": faker.address(),
        "username": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "total_cost": 3000
    }
    response = client.post("/dispatch/", json=fake_dispatch)
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_get_dispatch_unauthorized(test_db):
    response = client.get("/dispatch/1")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_list_dispatches_unauthorized(test_db):
    response = client.get("/dispatch/")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_delete_dispatch_unauthorized(test_db):
    response = client.delete("/dispatch/1")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"
