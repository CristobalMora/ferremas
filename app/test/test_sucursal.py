import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.sucursal import models, schemas
from app.domain.user.models import User
from database import Base, get_db
from faker import Faker
from app.domain.user.service import create_access_token, get_password_hash

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
def admin_token():
    fake_admin = {
        "nombre": faker.name(),
        "correo": faker.email(),
        "password": "adminpassword",
        "role": "Administrador"
    }
    db = TestingSessionLocal()
    hashed_password = get_password_hash(fake_admin["password"])
    db_admin = User(
        nombre=fake_admin["nombre"],
        correo=fake_admin["correo"],
        hashed_password=hashed_password,
        role=fake_admin["role"]
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    db.close()

    token = create_access_token(data={"sub": fake_admin["correo"]})
    return token

@pytest.fixture(scope="module")
def test_sucursal(admin_token):
    fake_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }
    response = client.post(
        "/sucursales/",
        json=fake_sucursal,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    return response.json()

def test_create_sucursal(test_db, admin_token):
    fake_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }
    response = client.post(
        "/sucursales/",
        json=fake_sucursal,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == fake_sucursal["nombre"]
    assert response.json()["direccion"] == fake_sucursal["direccion"]
    assert response.json()["telefono"] == fake_sucursal["telefono"]

def test_read_sucursal(test_db, test_sucursal, admin_token):
    sucursal_id = test_sucursal["id"]
    response = client.get(f"/sucursales/{sucursal_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["nombre"] == test_sucursal["nombre"]
    assert response.json()["direccion"] == test_sucursal["direccion"]
    assert response.json()["telefono"] == test_sucursal["telefono"]

def test_read_sucursales(test_db, admin_token):
    response = client.get("/sucursales/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_sucursal(test_db, test_sucursal, admin_token):
    sucursal_id = test_sucursal["id"]
    updated_sucursal = {
        "nombre": "Updated Sucursal",
        "direccion": test_sucursal["direccion"],
        "telefono": test_sucursal["telefono"]
    }
    response = client.put(
        f"/sucursales/{sucursal_id}",
        json=updated_sucursal,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == updated_sucursal["nombre"]

def test_delete_sucursal(test_db, test_sucursal, admin_token):
    sucursal_id = test_sucursal["id"]
    response = client.delete(f"/sucursales/{sucursal_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {"detail": "Sucursal deleted"}

def test_create_sucursal_unauthorized(test_db):
    fake_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }
    response = client.post(
        "/sucursales/",
        json=fake_sucursal
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_sucursal_unauthorized(test_db, admin_token):
    fake_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }
    create_response = client.post(
        "/sucursales/",
        json=fake_sucursal,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 200
    sucursal_id = create_response.json()["id"]

    updated_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }

    response = client.put(
        f"/sucursales/{sucursal_id}",
        json=updated_sucursal
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_sucursal_unauthorized(test_db, admin_token):
    fake_sucursal = {
        "nombre": faker.company(),
        "direccion": faker.address(),
        "telefono": faker.phone_number()
    }
    create_response = client.post(
        "/sucursales/",
        json=fake_sucursal,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 200
    sucursal_id = create_response.json()["id"]

    response = client.delete(
        f"/sucursales/{sucursal_id}"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
