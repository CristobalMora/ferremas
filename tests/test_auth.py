from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from Ferremas.sql_app import schemas, models, crud
from Ferremas.sql_app.database import SessionLocal, Base
from Ferremas.sql_app.dependencies import get_db
from main import app
import pytest

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=db.get_bind())
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=db.get_bind())

def test_create_user(db: Session):
    user_data = schemas.UserCreate(username="testuser", email="testuser@example.com", password="password", role="user")
    user = crud.create_user(db, user=user_data)
    assert user.email == "testuser@example.com"

def test_login_for_access_token(db: Session):
    user_data = schemas.UserCreate(username="testuser", email="testuser@example.com", password="password", role="user")
    crud.create_user(db, user=user_data)

    response = client.post("/auth/token", data={"username": "testuser@example.com", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
