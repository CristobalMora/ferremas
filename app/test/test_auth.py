import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
def fake_user():
    return {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": "password123",
        "role": "Cliente"
    }

@pytest.fixture(scope="module")
def access_token(test_client, fake_user):
    # Crear el usuario
    response = test_client.post(
        "/users/",
        json=fake_user
    )
    assert response.status_code == 200
    # Obtener el token
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
