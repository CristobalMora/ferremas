import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.user import models
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

def test_create_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": fake.password(),
        "role": "Cliente"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == user_data["nombre"]
    assert data["correo"] == user_data["correo"]
    assert data["role"] == user_data["role"]
    assert "id" in data

def test_read_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": fake.password(),
        "role": "Vendedor"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    user_id = response.json()["id"]
    response = test_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == user_data["nombre"]
    assert data["correo"] == user_data["correo"]
    assert data["role"] == user_data["role"]
    assert data["id"] == user_id

def test_read_users(test_client):
    response = test_client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": fake.password(),
        "role": "Administrador"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    user_id = response.json()["id"]
    updated_user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "role": "Bodega"
    }
    response = test_client.put(
        f"/users/{user_id}",
        json=updated_user_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == updated_user_data["nombre"]
    assert data["correo"] == updated_user_data["correo"]
    assert data["role"] == updated_user_data["role"]
    assert data["id"] == user_id

def test_delete_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": fake.password(),
        "role": "Cliente"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    user_id = response.json()["id"]
    response = test_client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    response = test_client.get(f"/users/{user_id}")
    assert response.status_code == 404
