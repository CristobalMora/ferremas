import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.dispatch import service, models, schemas
from fastapi import HTTPException
from pydantic import ValidationError

def test_create_dispatch_service():
    db = MagicMock(spec=Session)
    dispatch_data = schemas.DispatchCreate(address="123 Main St", username="john_doe", email="john@example.com", phone="555-1234")
    user_id = 1

    with patch.object(db, 'add') as mock_add, \
         patch.object(db, 'commit') as mock_commit, \
         patch.object(db, 'refresh') as mock_refresh:
        
        result = service.create_dispatch(db, dispatch_data, user_id)
        
        # Verificar que se haya creado correctamente
        created_dispatch = models.Dispatch(address=dispatch_data.address, username=dispatch_data.username, email=dispatch_data.email, phone=dispatch_data.phone, user_id=user_id, total_cost=3000)
        
        # Verificar las llamadas a los mocks
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()
        
        # Verificar que el dispatch creado tenga los valores esperados
        assert result.address == created_dispatch.address
        assert result.username == created_dispatch.username
        assert result.email == created_dispatch.email
        assert result.phone == created_dispatch.phone
        assert result.user_id == created_dispatch.user_id
        assert result.total_cost == created_dispatch.total_cost

def test_get_dispatch_service():
    db = MagicMock(spec=Session)
    dispatch_id = 1
    expected_dispatch = models.Dispatch(id=dispatch_id, address="123 Main St", username="john_doe", email="john@example.com", phone="555-1234", user_id=1, total_cost=3000)
    
    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = expected_dispatch
        result = service.get_dispatch(db, dispatch_id)
        assert result == expected_dispatch

def test_update_dispatch_service():
    db = MagicMock(spec=Session)
    dispatch_id = 1
    dispatch_update = schemas.DispatchCreate(address="456 Elm St", username="jane_doe", email="jane@example.com", phone="555-5678")
    existing_dispatch = models.Dispatch(id=dispatch_id, address="123 Main St", username="john_doe", email="john@example.com", phone="555-1234", user_id=1, total_cost=3000)
    
    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = existing_dispatch
        with patch.object(db, 'commit') as mock_commit:
            result = service.update_dispatch(db, dispatch_id, dispatch_update)
            mock_commit.assert_called_once()
            assert result.address == dispatch_update.address
            assert result.username == dispatch_update.username
            assert result.email == dispatch_update.email
            assert result.phone == dispatch_update.phone

def test_delete_dispatch_service():
    db = MagicMock(spec=Session)
    dispatch_id = 1
    existing_dispatch = models.Dispatch(id=dispatch_id, address="123 Main St", username="john_doe", email="john@example.com", phone="555-1234", user_id=1, total_cost=3000)
    
    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = existing_dispatch
        with patch.object(db, 'delete') as mock_delete, patch.object(db, 'commit') as mock_commit:
            result = service.delete_dispatch(db, dispatch_id)
            mock_delete.assert_called_once_with(existing_dispatch)
            mock_commit.assert_called_once()
            assert result == existing_dispatch

def test_list_dispatches_service():
    db = MagicMock(spec=Session)
    user_id = 1
    expected_dispatches = [
        models.Dispatch(id=1, address="123 Main St", username="john_doe", email="john@example.com", phone="555-1234", user_id=user_id, total_cost=3000),
        models.Dispatch(id=2, address="456 Elm St", username="jane_doe", email="jane@example.com", phone="555-5678", user_id=user_id, total_cost=3000)
    ]
    
    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.offset.return_value.limit.return_value.all.return_value = expected_dispatches
        result = service.list_dispatches(db, user_id, skip=0, limit=10)
        assert len(result) == len(expected_dispatches)
        for res_dispatch, exp_dispatch in zip(result, expected_dispatches):
            assert res_dispatch.id == exp_dispatch.id
            assert res_dispatch.address == exp_dispatch.address
            assert res_dispatch.username == exp_dispatch.username
            assert res_dispatch.email == exp_dispatch.email
            assert res_dispatch.phone == exp_dispatch.phone
            assert res_dispatch.total_cost == exp_dispatch.total_cost

def test_get_dispatch_not_found():
    db = MagicMock(spec=Session)
    dispatch_id = 1

    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.get_dispatch(db, dispatch_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Dispatch not found"

def test_update_dispatch_not_found():
    db = MagicMock(spec=Session)
    dispatch_id = 1
    dispatch_update = schemas.DispatchCreate(address="456 Elm St", username="jane_doe", email="jane@example.com", phone="555-5678")

    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.update_dispatch(db, dispatch_id, dispatch_update)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Dispatch not found"

def test_delete_dispatch_not_found():
    db = MagicMock(spec=Session)
    dispatch_id = 1

    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.delete_dispatch(db, dispatch_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Dispatch not found"

def test_list_dispatches_empty():
    db = MagicMock(spec=Session)
    user_id = 1

    with patch.object(db.query(models.Dispatch), 'filter') as mock_filter:
        mock_filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        result = service.list_dispatches(db, user_id, skip=0, limit=10)
        assert result == []

def test_create_dispatch_invalid_data():
    db = MagicMock(spec=Session)
    invalid_dispatch = {"address": None, "username": None, "email": "invalid-email", "phone": None}
    user_id = 1

    with pytest.raises(ValidationError):
        schemas.DispatchCreate(**invalid_dispatch)
