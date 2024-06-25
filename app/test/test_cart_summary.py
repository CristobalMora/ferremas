import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.domain.cart import models as cart_models
from app.domain.sales import models as sales_models
from app.domain.inventory import models as inventory_models
from app.domain.user.models import User
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
    fake_user.update(response.json())
    return fake_user

@pytest.fixture(scope="module")
def token(test_user):
    response = client.post(
        "/token",
        data={"username": test_user["correo"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def test_cart_item(test_db, test_user):
    db = TestingSessionLocal()

    # Crear un producto de inventario
    fake_inventory = inventory_models.Inventory(
        product_name=faker.word(),
        description=faker.text(),  # Ajustar para usar el nombre correcto del atributo
        price=faker.pyfloat(min_value=1, max_value=100, right_digits=2),
        quantity=faker.random_int(min=1, max=100)
    )
    db.add(fake_inventory)
    db.commit()
    db.refresh(fake_inventory)

    # Crear una venta
    fake_sale = sales_models.Sale(
        product_id=fake_inventory.id,
        price=fake_inventory.price
    )
    db.add(fake_sale)
    db.commit()
    db.refresh(fake_sale)

    # Crear un ítem de carrito
    fake_cart_item = cart_models.CartItem(
        user_id=test_user["id"],
        sale_id=fake_sale.id,
        quantity=faker.random_int(min=1, max=10)
    )
    db.add(fake_cart_item)
    db.commit()
    db.refresh(fake_cart_item)

    db.close()
    return fake_cart_item

def test_get_cart_summary(test_db, token, test_cart_item):
    response = client.get(
        "/cart_summary/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "items" in data
    assert "total_amount" in data
    assert len(data["items"]) > 0
    assert data["total_amount"] > 0

def test_get_cart_summary_unauthorized(test_db):
    response = client.get("/cart_summary/")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"
