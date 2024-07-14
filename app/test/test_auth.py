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
from jose import jwt
from datetime import datetime, timedelta, timezone

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

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

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
    return fake_user

def test_login_for_access_token_success(test_db, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

def test_login_for_access_token_failure(test_db):
    response = client.post(
        "/token",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_access_protected_route_with_valid_token(test_db, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["correo"] == test_user["correo"]

def test_access_protected_route_without_token(test_db):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_access_protected_route_with_invalid_token(test_db):
    invalid_token = "invalidtoken"
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_access_protected_route_with_expired_token(test_db, test_user):
    
    expired_token = jwt.encode({
        "sub": test_user["correo"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_access_protected_route_with_manipulated_token(test_db, test_user):
    
    valid_token = jwt.encode({
        "sub": test_user["correo"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }, SECRET_KEY, algorithm=ALGORITHM)
    manipulated_token = valid_token + "manipulated"

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {manipulated_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_token_generation(test_db, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    token = response.json()
    decoded_token = jwt.decode(token["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == test_user["correo"]
