import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.domain.sales import service, repository, schemas, models
from fastapi import HTTPException

# Test repository functions
def test_create_sale_repository():
    db = MagicMock(spec=Session)
    sale = schemas.SaleCreate(product_id=1, price=20.5)
    db_sale = models.Sale(id=1, **sale.dict())

    with patch.object(db, 'add') as mock_add:
        with patch.object(db, 'commit') as mock_commit:
            with patch.object(db, 'refresh') as mock_refresh:
                result = repository.create_sale(db, sale)
                mock_add.assert_called_once_with(result)
                mock_commit.assert_called_once()
                mock_refresh.assert_called_once_with(result)
                assert result.product_id == sale.product_id
                assert result.price == sale.price

def test_get_sales_repository():
    db = MagicMock(spec=Session)
    expected_sales = [
        models.Sale(id=1, product_id=1, price=20.5),
        models.Sale(id=2, product_id=2, price=30.0)
    ]
    db.query().offset().limit().all.return_value = expected_sales
    actual_sales = repository.get_sales(db, skip=0, limit=10)
    assert actual_sales == expected_sales

# Test service functions
def test_create_sale_service():
    db = MagicMock(spec=Session)
    sale = schemas.SaleCreate(product_id=1, price=20.5)
    current_user = MagicMock()
    current_user.role = "Vendedor"
    db_sale = models.Sale(id=1, **sale.dict())

    with patch.object(repository, 'create_sale', return_value=db_sale):
        result = service.create_sale(db, sale, current_user)
        assert result.product_id == db_sale.product_id
        assert result.price == db_sale.price

def test_create_sale_service_not_authorized():
    db = MagicMock(spec=Session)
    sale = schemas.SaleCreate(product_id=1, price=20.5)
    current_user = MagicMock()
    current_user.role = "Cliente"
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_sale(db, sale, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to add sale items"

def test_get_sales_service():
    db = MagicMock(spec=Session)
    expected_sales = [
        models.Sale(id=1, product_id=1, price=20.5),
        models.Sale(id=2, product_id=2, price=30.0)
    ]
    with patch.object(repository, 'get_sales', return_value=expected_sales):
        result = service.get_sales(db, skip=0, limit=10)
        assert result == expected_sales

def test_get_sale_service():
    db = MagicMock(spec=Session)
    sale_id = 1
    expected_sale = models.Sale(id=sale_id, product_id=1, price=20.5)
    with patch.object(repository, 'get_sale', return_value=expected_sale):
        result = service.get_sale(db, sale_id)
        assert result.product_id == expected_sale.product_id
        assert result.price == expected_sale.price

def test_get_sale_service_not_found():
    db = MagicMock(spec=Session)
    sale_id = 1
    with patch.object(repository, 'get_sale', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            service.get_sale(db, sale_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Sale not found"

def test_update_sale_service():
    db = MagicMock(spec=Session)
    sale_id = 1
    sale_update = schemas.SaleCreate(product_id=2, price=25.0)
    current_user = MagicMock()
    current_user.role = "Vendedor"
    db_sale = models.Sale(id=sale_id, product_id=1, price=20.5)

    with patch.object(repository, 'get_sale', return_value=db_sale):
        with patch.object(db, 'commit') as mock_commit:
            with patch.object(db, 'refresh') as mock_refresh:
                result = service.update_sale(db, sale_id, sale_update, current_user)
                mock_commit.assert_called_once()
                mock_refresh.assert_called_once_with(result)
                assert result.product_id == sale_update.product_id
                assert result.price == sale_update.price

def test_update_sale_service_not_authorized():
    db = MagicMock(spec=Session)
    sale_id = 1
    sale_update = schemas.SaleCreate(product_id=2, price=25.0)
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.update_sale(db, sale_id, sale_update, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update sale items"

def test_delete_sale_service():
    db = MagicMock(spec=Session)
    sale_id = 1
    current_user = MagicMock()
    current_user.role = "Vendedor"
    db_sale = models.Sale(id=sale_id, product_id=1, price=20.5)

    with patch.object(repository, 'get_sale', return_value=db_sale):
        with patch.object(repository, 'delete_sale', return_value=db_sale):
            result = service.delete_sale(db, sale_id, current_user)
            assert result == db_sale

def test_delete_sale_service_not_authorized():
    db = MagicMock(spec=Session)
    sale_id = 1
    current_user = MagicMock()
    current_user.role = "Cliente"

    with pytest.raises(HTTPException) as exc_info:
        service.delete_sale(db, sale_id, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to delete sale items"
