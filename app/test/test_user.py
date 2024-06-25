import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.user import models, schemas
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

print("test_user.py: OAuth2PasswordBearer initialized")

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
    return response.json()  # Devuelve el usuario creado incluyendo el ID

def test_create_user(test_db):
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
    data = response.json()
    assert data["correo"] == fake_user["correo"]
    assert "id" in data

def test_create_user_duplicate_email(test_db, test_user):
    duplicate_user = {
        "nombre": faker.name(),
        "correo": test_user["correo"],  # Same email as test_user
        "password": faker.password(),
        "role": "Cliente"
    }
    response = client.post(
        "/users/",
        json=duplicate_user,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_read_user(test_db, test_user):
    user_id = test_user["id"]  # Usa el ID del usuario de prueba
    
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["correo"] == test_user["correo"]

def test_read_user_not_found(test_db):
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_read_users(test_db):
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_user(test_db, test_user):
    user_id = test_user["id"]  # Usa el ID del usuario de prueba

    updated_user = {
        "nombre": faker.name(),
        "correo": faker.email(),
        "role": "Cliente"
    }
    response = client.put(
        f"/users/{user_id}",
        json=updated_user,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["correo"] == updated_user["correo"]

def test_update_user_not_found(test_db):
    updated_user = {
        "nombre": faker.name(),
        "correo": faker.email(),
        "role": "Cliente"
    }
    response = client.put(
        "/users/99999",
        json=updated_user,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_delete_user(test_db, test_user):
    # Crear un nuevo usuario para eliminar
    fake_user_to_delete = {
        "nombre": faker.name(),
        "correo": faker.email(),
        "password": faker.password(),
        "role": "Cliente"
    }
    create_response = client.post(
        "/users/",
        json=fake_user_to_delete,
    )
    assert create_response.status_code == 200
    user_to_delete = create_response.json()
    user_id = user_to_delete["id"]

    # Eliminar el usuario creado
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["correo"] == fake_user_to_delete["correo"]

    # Verificar que el usuario ha sido eliminado
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
