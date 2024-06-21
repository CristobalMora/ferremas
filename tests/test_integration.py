import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cart_process():
    # Registro de usuario
    response = client.post("/auth/register", json={
        "username": "integrationuser",
        "email": "integrationuser@example.com",
        "password": "password123",
        "role": "client"
    })
    assert response.status_code == 201

    # Login y obtención del token
    response = client.post("/auth/token", data={
        "username": "integrationuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Añadir producto al carrito
    response = client.post("/cart_items/", json={
        "product_id": 1,
        "quantity": 2
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Verificar el carrito
    response = client.get("/cart_items/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0
