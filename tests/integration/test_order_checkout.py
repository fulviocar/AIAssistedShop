from decimal import Decimal

import pytest
from app.auth import create_customer_access_token
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app import create_app, db
from app.models import (
    Cart,
    CartItem,
    Category,
    Customer,
    Order,
    OrderItem,
    Product,
)


@pytest.fixture
def database_uri(tmp_path):
    # A file per test keeps the test database separate from the
    # development database and from every other test.
    return f"sqlite:///{tmp_path / 'checkout_test.db'}"


@pytest.fixture
def app(database_uri):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "JWT_SECRET_KEY": "integration-test-secret-key-32-bytes-min",
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def checkout_records(app):
    with app.app_context():
        customer = Customer(
            name="Alice Martin",
            email="alice.martin@example.com",
        )
        customer.set_password("secret123")

        category = Category(name="Office")

        product = Product(
            name="Desk Lamp",
            description="LED desk lamp with adjustable arm",
            price=Decimal("15.00"),
            stock_quantity=10,
            category=category,
        )

        cart = Cart(customer=customer)

        cart_item = CartItem(
            cart=cart,
            product=product,
            quantity=2,
        )

        db.session.add_all([customer, category, product, cart, cart_item])
        db.session.commit()

        return {
            "customer_id": customer.id,
            "product_id": product.id,
            "cart_item_id": cart_item.id,
        }


@pytest.fixture
def auth_headers(app, checkout_records):
    with app.app_context():
        token = create_customer_access_token(
            checkout_records["customer_id"]
        )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def committed_session(database_uri):
    # A separate engine opens its own connection, so it only sees data
    # that the application actually committed to the test database.
    engine = create_engine(database_uri)
    session = Session(engine)

    yield session

    session.close()
    engine.dispose()


@pytest.mark.integration
def test_checkout_completes_order_end_to_end(
    client,
    checkout_records,
    auth_headers,
    committed_session,
):
    # Arrange
    customer_id = checkout_records["customer_id"]
    product_id = checkout_records["product_id"]
    cart_item_id = checkout_records["cart_item_id"]

    # Act
    response = client.post(
        "/api/customers/me/orders/checkout",
        headers=auth_headers,
    )

    # Assert - API response
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data["customer_id"] == customer_id
    assert response_data["status"] == "confirmed"
    assert response_data["total_amount"] == "30.00"
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["product_id"] == product_id
    assert response_data["items"][0]["quantity"] == 2
    assert response_data["items"][0]["unit_price"] == "15.00"

    # Assert - order committed with the correct total and status
    order = committed_session.scalar(
        select(Order).where(Order.customer_id == customer_id)
    )
    assert order is not None
    assert order.id == response_data["id"]
    assert order.status == "confirmed"
    assert order.total_amount == Decimal("30.00")

    # Assert - order item committed
    order_items = committed_session.scalars(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()
    assert len(order_items) == 1
    assert order_items[0].product_id == product_id
    assert order_items[0].quantity == 2
    assert order_items[0].unit_price == Decimal("15.00")

    # Assert - inventory reduced by the purchased quantity
    product = committed_session.get(Product, product_id)
    assert product.stock_quantity == 8

    # Assert - cart item removed
    assert committed_session.get(CartItem, cart_item_id) is None
