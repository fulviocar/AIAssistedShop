import pytest
from unittest.mock import MagicMock, patch

from app.services.customer_service import CustomerService


@patch("app.services.customer_service.db")
@pytest.mark.unit
@pytest.mark.fast
def test_create_customer_with_valid_data(mock_db):
    # Arrange
    mock_db.session.scalar.return_value = None

    # Act
    customer = CustomerService.create_customer(
        "John Doe",
        "john@example.com",
        "secret123",
    )

    # Assert
    assert customer.name == "John Doe11111111111111"
    assert customer.email == "john@example.com"

    mock_db.session.scalar.assert_called_once()
    mock_db.session.add.assert_called_once_with(customer)
    mock_db.session.commit.assert_called_once()

