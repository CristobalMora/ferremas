import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.sucursal import service, repository, schemas, models
from fastapi import HTTPException

def test_create_sucursal_service():
    db = MagicMock(spec=Session)
    sucursal = schemas.SucursalCreate(nombre="Sucursal Test", direccion="Dirección Test", telefono="123456789")
    current_user = MagicMock()
    current_user.role = "Administrador"
    db_sucursal = models.Sucursal(id=1, **sucursal.model_dump())

    with patch.object(repository, 'create_sucursal', return_value=db_sucursal):
        result = service.create_sucursal(db, sucursal, current_user)
        assert result == db_sucursal

def test_create_sucursal_service_not_authorized():
    db = MagicMock(spec=Session)
    sucursal = schemas.SucursalCreate(nombre="Sucursal Test", direccion="Dirección Test", telefono="123456789")
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.create_sucursal(db, sucursal, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Operation not permitted"

def test_update_sucursal_service():
    db = MagicMock(spec=Session)
    sucursal_id = 1
    sucursal_update = schemas.SucursalCreate(nombre="Sucursal Updated", direccion="Dirección Updated", telefono="987654321")
    current_user = MagicMock()
    current_user.role = "Administrador"
    db_sucursal = models.Sucursal(id=sucursal_id, nombre="Sucursal Test", direccion="Dirección Test", telefono="123456789")

    with patch.object(repository, 'get_sucursal', return_value=db_sucursal):
        with patch.object(repository, 'update_sucursal', return_value=db_sucursal):
            result = service.update_sucursal(db, sucursal_id, sucursal_update, current_user)
            assert result == db_sucursal

def test_update_sucursal_service_not_authorized():
    db = MagicMock(spec=Session)
    sucursal_id = 1
    sucursal_update = schemas.SucursalCreate(nombre="Sucursal Updated", direccion="Dirección Updated", telefono="987654321")
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.update_sucursal(db, sucursal_id, sucursal_update, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Operation not permitted"

def test_delete_sucursal_service():
    db = MagicMock(spec=Session)
    sucursal_id = 1
    current_user = MagicMock()
    current_user.role = "Administrador"
    db_sucursal = models.Sucursal(id=sucursal_id, nombre="Sucursal Test", direccion="Dirección Test", telefono="123456789")

    with patch.object(repository, 'get_sucursal', return_value=db_sucursal):
        with patch.object(repository, 'delete_sucursal', return_value=db_sucursal):
            result = service.delete_sucursal(db, sucursal_id, current_user)
            assert result == db_sucursal

def test_delete_sucursal_service_not_authorized():
    db = MagicMock(spec=Session)
    sucursal_id = 1
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.delete_sucursal(db, sucursal_id, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Operation not permitted"
