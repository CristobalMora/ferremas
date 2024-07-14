import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.cart import service, models, schemas
from fastapi import HTTPException
from pydantic import ValidationError

def test_create_cart_item_service():
    db = MagicMock(spec=Session)
    cart_item = schemas.CartItemCreate(sale_id=1, quantity=5)
    user_id = 1
    db_cart_item = models.CartItem(id=1, user_id=user_id, sale_id=cart_item.sale_id, quantity=cart_item.quantity)

    with patch.object(db, 'add') as mock_add, \
         patch.object(db, 'commit') as mock_commit, \
         patch.object(db, 'refresh') as mock_refresh:
        
        result = service.create_cart_item(db, cart_item, user_id)
        
        
        created_item = models.CartItem(sale_id=cart_item.sale_id, quantity=cart_item.quantity, user_id=user_id)
        
        
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()
        
        
        assert result.sale_id == created_item.sale_id
        assert result.quantity == created_item.quantity
        assert result.user_id == created_item.user_id

def test_get_cart_items_service():
    db = MagicMock(spec=Session)
    user_id = 1
    expected_cart_items = [
        models.CartItem(id=1, user_id=user_id, sale_id=1, quantity=5),
        models.CartItem(id=2, user_id=user_id, sale_id=2, quantity=3)
    ]
    
    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.all.return_value = expected_cart_items
        result = service.get_cart_items(db, user_id)
        assert len(result) == len(expected_cart_items)
        for res_item, exp_item in zip(result, expected_cart_items):
            assert res_item.id == exp_item.id
            assert res_item.sale_id == exp_item.sale_id
            assert res_item.quantity == exp_item.quantity

def test_delete_cart_item_service():
    db = MagicMock(spec=Session)
    user_id = 1
    item_id = 1
    db_cart_item = models.CartItem(id=item_id, user_id=user_id, sale_id=1, quantity=5)

    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = db_cart_item
        with patch.object(db, 'delete') as mock_delete, patch.object(db, 'commit') as mock_commit:
            result = service.delete_cart_item(db, item_id, user_id)
            mock_delete.assert_called_once_with(db_cart_item)
            mock_commit.assert_called_once()
            assert result == db_cart_item


def test_update_cart_item_service():
    db = MagicMock(spec=Session)
    user_id = 1
    item_id = 1
    cart_item_update = schemas.CartItemCreate(sale_id=2, quantity=10)
    db_cart_item = models.CartItem(id=item_id, user_id=user_id, sale_id=1, quantity=5)

    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = db_cart_item
        with patch.object(db, 'commit') as mock_commit:
            result = service.update_cart_item(db, item_id, cart_item_update, user_id)
            mock_commit.assert_called_once()
            assert result.sale_id == cart_item_update.sale_id
            assert result.quantity == cart_item_update.quantity

def test_get_cart_item_service():
    db = MagicMock(spec=Session)
    user_id = 1
    item_id = 1
    db_cart_item = models.CartItem(id=item_id, user_id=user_id, sale_id=1, quantity=5)

    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = db_cart_item
        result = service.get_cart_item(db, item_id, user_id)
        assert result == db_cart_item

def test_create_cart_item_invalid_data():
    db = MagicMock(spec=Session)
   
    cart_item = {"sale_id": None, "quantity": None}
    user_id = 1

    with pytest.raises(ValidationError):
        schemas.CartItemCreate(**cart_item)


def test_update_cart_item_not_found():
    db = MagicMock(spec=Session)
    user_id = 1
    item_id = 999
    cart_item_update = schemas.CartItemCreate(sale_id=2, quantity=10)

    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.update_cart_item(db, item_id, cart_item_update, user_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Cart item not found"


def test_get_cart_item_not_found():
    db = MagicMock(spec=Session)
    user_id = 1
    item_id = 999

    with patch.object(db.query(models.CartItem), 'filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.get_cart_item(db, item_id, user_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Cart item not found"