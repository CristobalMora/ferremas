import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from Ferremas.sql_app import schemas, crud

def test_login_for_access_token(test_client: TestClient, fake_data):
    # Usa credenciales únicas para evitar duplicados
    user_data = schemas.UserCreate(username="newuser", email="newuser@example.com", password="password", role="user")
    response = test_client.post("/auth/register", json=user_data.dict())
    assert response.status_code == 201
    login_data = {"username": user_data.username, "password": user_data.password}
    response = test_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
