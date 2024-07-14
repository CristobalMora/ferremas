import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.inventory import service, repository, schemas, models
from fastapi import HTTPException

# Test repository functions
def test_create_inventory_item_repository():
    db = MagicMock(spec=Session)
    item = schemas.InventoryCreate(product_name="Hammer", description="For hammering", quantity=10)
    db_item = models.Inventory(id=1, **item.model_dump())

    with patch.object(db, 'add') as mock_add:
        with patch.object(db, 'commit') as mock_commit:
            with patch.object(db, 'refresh') as mock_refresh:
                result = repository.create_inventory_item(db, item)
                mock_add.assert_called_once_with(result)
                mock_commit.assert_called_once()
                mock_refresh.assert_called_once_with(result)
                assert result.product_name == item.product_name
                assert result.description == item.description
                assert result.quantity == item.quantity

def test_get_inventory_item_repository():
    db = MagicMock(spec=Session)
    item_id = 1
    expected_item = models.Inventory(id=item_id, product_name="Hammer", description="For hammering", quantity=10)
    db.query().filter().first.return_value = expected_item
    actual_item = repository.get_inventory_item(db, item_id)
    assert actual_item == expected_item

def test_update_inventory_item_repository():
    db = MagicMock(spec=Session)
    db_item = models.Inventory(id=1, product_name="Hammer", description="For hammering", quantity=10)
    item_update = schemas.InventoryCreate(product_name="Hammer Updated", description="For hammering updated", quantity=15)
    
    with patch.object(db, 'commit') as mock_commit:
        with patch.object(db, 'refresh') as mock_refresh:
            result = repository.update_inventory_item(db, db_item, item_update)
            assert result.product_name == item_update.product_name
            assert result.description == item_update.description
            assert result.quantity == item_update.quantity
            mock_commit.assert_called_once()
            mock_refresh.assert_called_once_with(db_item)

def test_delete_inventory_item_repository():
    db = MagicMock(spec=Session)
    db_item = models.Inventory(id=1, product_name="Hammer", description="For hammering", quantity=10)

    with patch.object(db, 'delete') as mock_delete:
        with patch.object(db, 'commit') as mock_commit:
            repository.delete_inventory_item(db, db_item)
            mock_delete.assert_called_once_with(db_item)
            mock_commit.assert_called_once()

# Test service functions
def test_get_inventory_item_service():
    db = MagicMock(spec=Session)
    item_id = 1
    expected_item = models.Inventory(id=item_id, product_name="Hammer", description="For hammering", quantity=10)
    with patch.object(repository, 'get_inventory_item', return_value=expected_item):
        result = service.get_inventory_item(db, item_id)
        assert result == expected_item

def test_get_inventory_item_service_not_found():
    db = MagicMock(spec=Session)
    item_id = 1
    with patch.object(repository, 'get_inventory_item', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            service.get_inventory_item(db, item_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Inventory item not found"

def test_create_inventory_item_service():
    db = MagicMock(spec=Session)
    item = schemas.InventoryCreate(product_name="Hammer", description="For hammering", quantity=10)
    current_user = MagicMock()
    current_user.role = "Bodega"
    db_item = models.Inventory(id=1, **item.dict())

    with patch.object(repository, 'create_inventory_item', return_value=db_item):
        result = service.create_inventory_item(db, item, current_user)
        assert result == db_item

def test_create_inventory_item_service_not_authorized():
    db = MagicMock(spec=Session)
    item = schemas.InventoryCreate(product_name="Hammer", description="For hammering", quantity=10)
    current_user = MagicMock()
    current_user.role = "Cliente"
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_inventory_item(db, item, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to add inventory items"

def test_update_inventory_item_service():
    db = MagicMock(spec=Session)
    item_id = 1
    item_update = schemas.InventoryCreate(product_name="Hammer Updated", description="For hammering updated", quantity=15)
    current_user = MagicMock()
    current_user.role = "Bodega"
    db_item = models.Inventory(id=item_id, product_name="Hammer", description="For hammering", quantity=10)

    with patch.object(repository, 'get_inventory_item', return_value=db_item):
        with patch.object(repository, 'update_inventory_item', return_value=db_item):
            result = service.update_inventory_item(db, item_id, item_update, current_user)
            assert result == db_item

def test_update_inventory_item_service_not_authorized():
    db = MagicMock(spec=Session)
    item_id = 1
    item_update = schemas.InventoryCreate(product_name="Hammer Updated", description="For hammering updated", quantity=15)
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.update_inventory_item(db, item_id, item_update, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update inventory items"

def test_delete_inventory_item_service():
    db = MagicMock(spec=Session)
    item_id = 1
    quantity = 10
    current_user = MagicMock()
    current_user.role = "Bodega"
    db_item = models.Inventory(id=item_id, product_name="Hammer", description="For hammering", quantity=quantity)

    with patch.object(repository, 'get_inventory_item', return_value=db_item):
        with patch.object(repository, 'delete_inventory_item', return_value=db_item):
            result = service.delete_inventory_item(db, item_id, quantity, current_user)
            assert result == db_item

def test_delete_inventory_item_service_not_authorized():
    db = MagicMock(spec=Session)
    item_id = 1
    quantity = 10
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.delete_inventory_item(db, item_id, quantity, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to delete inventory items"
