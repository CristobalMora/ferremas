import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.user import models, schemas, repository, service

# Setup for password context
pwd_context = service.pwd_context

def test_verify_password():
    plain_password = "password123"
    hashed_password = pwd_context.hash(plain_password)
    assert service.verify_password(plain_password, hashed_password) == True

def test_get_password_hash():
    plain_password = "password123"
    hashed_password = service.get_password_hash(plain_password)
    assert pwd_context.verify(plain_password, hashed_password) == True

def test_create_user_repository():
    db = MagicMock(spec=Session)
    user = models.User(
        nombre="Juan Perez",
        correo="juan@example.com",
        hashed_password="hashed_password",
        role="Cliente"
    )
    repository.create_user(db, user)
    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)

def test_get_user_repository():
    db = MagicMock(spec=Session)
    user_id = 1
    expected_user = models.User(id=user_id, nombre="Juan Perez", correo="juan@example.com")
    db.query().filter().first.return_value = expected_user
    actual_user = repository.get_user(db, user_id)
    assert actual_user == expected_user

def test_update_user_repository():
    db = MagicMock(spec=Session)
    db_user = models.User(id=1, nombre="Juan Perez", correo="juan@example.com", role="Cliente")
    user_update = schemas.UserUpdate(nombre="Juan Updated", correo="juan_updated@example.com", role="Cliente")
    updated_user = repository.update_user(db, db_user, user_update)
    assert updated_user.nombre == user_update.nombre
    assert updated_user.correo == user_update.correo
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(db_user)

def test_delete_user_repository():
    db = MagicMock(spec=Session)
    db_user = models.User(id=1, nombre="Juan Perez", correo="juan@example.com")
    repository.delete_user(db, db_user)
    db.delete.assert_called_once_with(db_user)
    db.commit.assert_called_once()

def test_authenticate_user_success():
    db = MagicMock(spec=Session)
    email = "juan@example.com"
    password = "password123"
    hashed_password = pwd_context.hash(password)
    user = models.User(correo=email, hashed_password=hashed_password)
    db.query().filter().first.return_value = user
    authenticated_user = service.authenticate_user(db, email, password)
    assert authenticated_user == user

def test_authenticate_user_failure():
    db = MagicMock(spec=Session)
    email = "juan@example.com"
    password = "password123"
    db.query().filter().first.return_value = None
    authenticated_user = service.authenticate_user(db, email, password)
    assert authenticated_user == False
