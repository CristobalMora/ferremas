import pytest
from fastapi.testclient import TestClient
from conftest import create_fake_token  # Importa la función desde conftest.py

def test_cart_process(test_client: TestClient, fake_data):
    # Registro de usuario
    response = test_client.post("/auth/register", json={
        "username": "integrationuser",
        "email": "integrationuser@example.com",
        "password": "password123",
        "role": "client"
    })
    assert response.status_code == 201

    # Login
    login_data = {"username": "integrationuser", "password": "password123"}
    response = test_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # Agregar al carrito
    response = test_client.post("/cart_items/", headers=headers, json={"product_id": 1, "quantity": 2})
    assert response.status_code == 200

    # Ver carrito
    response = test_client.get("/cart_items/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Remover del carrito
    response = test_client.delete(f"/cart_items/1", headers=headers)
    assert response.status_code == 200
