import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.user import service, repository, schemas, models
from app.routers.auth import login_for_access_token, read_users_me
from fastapi import HTTPException, Depends
from jose import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




def test_verify_password():
    plain_password = "password123"
    hashed_password = service.get_password_hash(plain_password)
    assert service.verify_password(plain_password, hashed_password) == True

def test_get_password_hash():
    plain_password = "password123"
    hashed_password = service.get_password_hash(plain_password)
    assert service.verify_password(plain_password, hashed_password) == True

def test_authenticate_user_success():
    db = MagicMock(spec=Session)
    email = "juan@example.com"
    password = "password123"
    hashed_password = service.get_password_hash(password)
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

def test_create_access_token():
    data = {"sub": "juan@example.com"}
    expires_delta = timedelta(minutes=15)
    token = service.create_access_token(data, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == data["sub"]

def test_create_access_token_expired():
    data = {"sub": "juan@example.com"}
    expires_delta = timedelta(minutes=-15)  
    token = service.create_access_token(data, expires_delta)
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_get_current_user_failure():
    db = MagicMock(spec=Session)
    token = "invalidtoken"

    with pytest.raises(HTTPException) as exc_info:
        service.get_current_user(db, token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


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


def test_login_for_access_token_success():
    db = MagicMock(spec=Session)
    form_data = MagicMock()
    form_data.username = "juan@example.com"
    form_data.password = "password123"
    user = MagicMock()
    user.correo = form_data.username
    user.role = "Cliente"

    with patch('app.domain.user.service.authenticate_user', return_value=user):
        with patch('app.domain.user.service.create_access_token', return_value="fake_token"):
            result = login_for_access_token(db, form_data)
            assert result == {"access_token": "fake_token", "token_type": "bearer"}

def test_login_for_access_token_failure():
    db = MagicMock(spec=Session)
    form_data = MagicMock()
    form_data.username = "juan@example.com"
    form_data.password = "wrongpassword"

    with patch('app.domain.user.service.authenticate_user', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            login_for_access_token(db, form_data)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Incorrect username or password"

def test_read_users_me():
    current_user = MagicMock()
    current_user.correo = "juan@example.com"
    result = read_users_me(current_user)
    assert result.correo == "juan@example.com"

def test_invalid_token():
    db = MagicMock(spec=Session)
    token = "invalidtoken"

    with pytest.raises(HTTPException) as exc_info:
        service.get_current_user(db, token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
