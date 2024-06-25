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
def cliente_user(test_client):
    user_data = {
        "nombre": fake.name(),
        "correo": fake.email(),
        "password": "password123",
        "role": "Cliente"
    }
    response = test_client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 200
    return user_data

@pytest.fixture(scope="module")
def cliente_token(test_client, cliente_user):
    response = test_client.post(
        "/token",
        data={"username": cliente_user["correo"], "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_create_dispatch(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}
    dispatch_data = {
        "address": fake.address(),
        "username": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }
    response = test_client.post(
        "/dispatch/",
        json=dispatch_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["address"] == dispatch_data["address"]
    assert data["username"] == dispatch_data["username"]
    assert data["email"] == dispatch_data["email"]
    assert data["phone"] == dispatch_data["phone"]
    assert data["total_cost"] == 3000
    assert "id" in data

def test_get_dispatch(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}
    
    # Crear un despacho primero
    dispatch_data = {
        "address": fake.address(),
        "username": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }
    response = test_client.post(
        "/dispatch/",
        json=dispatch_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    dispatch = response.json()

    # Obtener detalles del despacho
    dispatch_id = dispatch["id"]
    response = test_client.get(
        f"/dispatch/{dispatch_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == dispatch_id
    assert data["address"] == dispatch["address"]
    assert data["username"] == dispatch["username"]
    assert data["email"] == dispatch["email"]
    assert data["phone"] == dispatch["phone"]

def test_update_dispatch(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}

    # Crear un despacho primero
    dispatch_data = {
        "address": fake.address(),
        "username": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }
    response = test_client.post(
        "/dispatch/",
        json=dispatch_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    dispatch = response.json()

    # Actualizar el despacho
    dispatch_id = dispatch["id"]
    update_data = {
        "address": fake.address(),
        "username": dispatch["username"],
        "email": dispatch["email"],
        "phone": dispatch.get("phone")
    }
    response = test_client.put(
        f"/dispatch/{dispatch_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == dispatch_id
    assert data["address"] == update_data["address"]
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]
    assert data["phone"] == update_data["phone"]

def test_delete_dispatch(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}

    # Crear un despacho primero
    dispatch_data = {
        "address": fake.address(),
        "username": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }
    response = test_client.post(
        "/dispatch/",
        json=dispatch_data,
        headers=headers
    )
    assert response.status_code == 200, response.text
    dispatch = response.json()

    # Eliminar el despacho
    dispatch_id = dispatch["id"]
    response = test_client.delete(
        f"/dispatch/{dispatch_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text

def test_list_dispatches(test_client, cliente_token):
    headers = {"Authorization": f"Bearer {cliente_token}"}

    # Crear algunos despachos
    for _ in range(3):
        dispatch_data = {
            "address": fake.address(),
            "username": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number()
        }
        response = test_client.post(
            "/dispatch/",
            json=dispatch_data,
            headers=headers
        )
        assert response.status_code == 200

    # Listar los despachos
    response = test_client.get("/dispatch/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 3

def test_create_dispatch_unauthorized(test_client):
    dispatch_data = {
        "address": fake.address(),
        "username": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }
    response = test_client.post(
        "/dispatch/",
        json=dispatch_data
    )
    assert response.status_code == 401

def test_get_dispatch_unauthorized(test_client):
    response = test_client.get("/dispatch/1")
    assert response.status_code == 401

def test_update_dispatch_unauthorized(test_client):
    update_data = {"address": fake.address()}
    response = test_client.put(
        "/dispatch/1",
        json=update_data
    )
    assert response.status_code == 401

def test_delete_dispatch_unauthorized(test_client):
    response = test_client.delete("/dispatch/1")
    assert response.status_code == 401
