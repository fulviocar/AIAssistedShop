from decimal import Decimal

from app import db
from app.models import Cart, CartItem, Customer, Product


class CartService:

    @staticmethod
    def get_or_create_cart(customer_id: int) -> Cart:
        customer = db.session.get(Customer, customer_id)

        if customer is None:
            raise ValueError("Customer not found")

        if customer.cart is not None:
            return customer.cart

        cart = Cart(customer=customer)

        db.session.add(cart)
        db.session.commit()

        return cart

    @staticmethod
    def add_item(
        customer_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        cart = CartService.get_or_create_cart(customer_id)

        product = db.session.get(Product, product_id)

        if product is None:
            raise ValueError("Product not found")

        if quantity > product.stock_quantity:
            raise ValueError("Insufficient stock")

        existing_item = db.session.scalar(
            db.select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
        )

        if existing_item is not None:

            new_quantity = existing_item.quantity + quantity

            if new_quantity > product.stock_quantity:
                raise ValueError("Insufficient stock")

            existing_item.quantity = new_quantity
            db.session.commit()

            return existing_item

        item = CartItem(
            cart=cart,
            product=product,
            quantity=quantity,
        )

        db.session.add(item)
        db.session.commit()

        return item

    @staticmethod
    def update_item(
        customer_id: int,
        item_id: int,
        quantity: int,
    ) -> CartItem:

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        cart = CartService.get_or_create_cart(customer_id)

        item = db.session.scalar(
            db.select(CartItem).where(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id,
            )
        )

        if item is None:
            raise ValueError("Cart item not found")

        if quantity > item.product.stock_quantity:
            raise ValueError("Insufficient stock")

        item.quantity = quantity

        db.session.commit()

        return item

    @staticmethod
    def remove_item(
        customer_id: int,
        item_id: int,
    ) -> None:

        cart = CartService.get_or_create_cart(customer_id)

        item = db.session.scalar(
            db.select(CartItem).where(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id,
            )
        )

        if item is None:
            raise ValueError("Cart item not found")

        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def clear_cart(customer_id: int) -> None:

        cart = CartService.get_or_create_cart(customer_id)

        for item in cart.items:
            db.session.delete(item)

        db.session.commit()

    @staticmethod
    def get_cart(customer_id: int) -> Cart:
        return CartService.get_or_create_cart(customer_id)

    @staticmethod
    def calculate_total(cart: Cart) -> Decimal:

        total = Decimal("0.00")

        for item in cart.items:
            total += item.product.price * item.quantity

        return total