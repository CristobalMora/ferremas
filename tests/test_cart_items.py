import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_to_cart_as_client():
    response = client.post("/cart_items/", json={"product_id": product_id, "quantity": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity"] == 2

def test_add_to_cart_as_non_client():
    db = TestingSessionLocal()
    non_client_user = models.User(username="nonclientuser", email="nonclient@example.com", hashed_password="password", role="vendedor")
    db.add(non_client_user)
    db.commit()
    db.refresh(non_client_user)

    response = client.post("/cart_items/", json={"product_id": product_id, "quantity": 2}, headers={"X-User-Id": non_client_user.id})
    assert response.status_code == 403

def test_remove_from_cart_as_client():
    response = client.post("/cart_items/", json={"product_id": product_id, "quantity": 2})
    assert response.status_code == 200
    cart_item_id = response.json()["id"]

    response = client.delete(f"/cart_items/{cart_item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cart_item_id

def test_remove_from_cart_as_non_client():
    db = TestingSessionLocal()
    non_client_user = models.User(username="nonclientuser", email="nonclient@example.com", hashed_password="password", role="vendedor")
    db.add(non_client_user)
    db.commit()
    db.refresh(non_client_user)

    response = client.delete("/cart_items/1", headers={"X-User-Id": non_client_user.id})
    assert response.status_code == 403

def test_view_cart_as_client():
    response = client.get("/cart_items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_view_cart_as_non_client():
    db = TestingSessionLocal()
    non_client_user = models.User(username="nonclientuser", email="nonclient@example.com", hashed_password="password", role="vendedor")
    db.add(non_client_user)
    db.commit()
    db.refresh(non_client_user)

    response = client.get("/cart_items/", headers={"X-User-Id": non_client_user.id})
    assert response.status_code == 403
