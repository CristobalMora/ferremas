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

@pytest.fixture(scope="module")
def fake_user():
    fake = Faker()
    return {
        "nombre": fake.name(),
        "correo": fake.email(),
        "role": "Cliente",
        "password": fake.password()
    }

@pytest.fixture(scope="module")
def access_token(test_client, fake_user):
    # Crear el usuario
    response = test_client.post(
        "/users/",
        json=fake_user
    )
    assert response.status_code == 200
    assert response.json() is not None
    
    # Autenticar al usuario
    response = test_client.post(
        "/token",
        data={"username": fake_user["correo"], "password": fake_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    return data["access_token"]

def test_create_user_for_auth(test_client, fake_user):
    response = test_client.post(
        "/users/",
        json=fake_user
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == fake_user["nombre"]
    assert data["correo"] == fake_user["correo"]
    assert data["role"] == fake_user["role"]
    assert "id" in data

def test_login_user(access_token):
    assert access_token is not None

def test_read_user_authenticated(test_client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["correo"] is not None
