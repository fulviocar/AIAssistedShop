from decimal import Decimal

from app import db
from app.models import Cart, CartItem, Customer, Order, OrderItem


class OrderService:

    @staticmethod
    def checkout(customer_id: int) -> Order:
        customer = db.session.get(Customer, customer_id)

        if customer is None:
            raise ValueError("Customer not found")

        cart = db.session.scalar(
            db.select(Cart).where(
                Cart.customer_id == customer_id
            )
        )

        if cart is None or not cart.items:
            raise ValueError("Cart is empty")

        try:
            total = Decimal("0.00")

            # Validate the entire cart before changing anything.
            for cart_item in cart.items:

                product = cart_item.product

                if cart_item.quantity <= 0:
                    raise ValueError(
                        "Cart contains an invalid quantity"
                    )

                if cart_item.quantity > product.stock_quantity:
                    raise ValueError(
                        f"Insufficient stock for product "
                        f"'{product.name}'"
                    )

            # Create the order.
            order = Order(
                customer=customer,
                status="pending",
                total_amount=Decimal("0.00"),
            )

            db.session.add(order)

            # Create order items and update inventory.
            for cart_item in cart.items:

                product = cart_item.product

                unit_price = product.price

                subtotal = unit_price * cart_item.quantity

                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                )

                db.session.add(order_item)

                product.stock_quantity -= cart_item.quantity

                total += subtotal

            order.total_amount = total
            order.status = "confirmed"

            # Remove all items from the cart.
            for cart_item in list(cart.items):
                db.session.delete(cart_item)

            db.session.commit()

            return order

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_order(
        customer_id: int,
        order_id: int,
    ) -> Order | None:

        return db.session.scalar(
            db.select(Order).where(
                Order.id == order_id,
                Order.customer_id == customer_id,
            )
        )

    @staticmethod
    def get_orders(customer_id: int) -> list[Order]:

        return db.session.scalars(
            db.select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.id)
        ).all()