import pytest
from fastapi.testclient import TestClient
from conftest import create_fake_token  # Importa la función desde conftest.py

def test_add_to_cart_as_client(test_client: TestClient, fake_data):
    token = create_fake_token(user_id=fake_data['user_id'], username="testuser")
    headers = {"Authorization": f"Bearer {token}"}

    response = test_client.post("/cart_items/", json={"product_id": fake_data['product_id'], "quantity": 2}, headers=headers)
    assert response.status_code == 200

def test_add_to_cart_as_non_client(test_db):
    db = test_db
    # Resto de la prueba, usando `db`

def test_remove_from_cart_as_client(test_client: TestClient, fake_data):
    token = create_fake_token(user_id=fake_data['user_id'], username="testuser")
    headers = {"Authorization": f"Bearer {token}"}

    response = test_client.post("/cart_items/", json={"product_id": fake_data['product_id'], "quantity": 2}, headers=headers)
    assert response.status_code == 200
    response = test_client.delete(f"/cart_items/{fake_data['product_id']}", headers=headers)
    assert response.status_code == 200

def test_view_cart_as_client(test_client: TestClient, fake_data):
    token = create_fake_token(user_id=fake_data['user_id'], username="testuser")
    headers = {"Authorization": f"Bearer {token}"}

    response = test_client.get("/cart_items/", headers=headers)
    assert response.status_code == 200

def test_view_cart_as_non_client(test_db):
    db = test_db
    # Resto de la prueba, usando `db`
