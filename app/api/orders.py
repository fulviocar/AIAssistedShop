from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.order_service import OrderService


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/customers/me/orders",
)


def get_current_customer_id() -> int:
    return int(get_jwt_identity())


def order_to_dict(order):
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": str(order.total_amount),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "subtotal": str(
                    item.unit_price * item.quantity
                ),
            }
            for item in order.items
        ],
    }


@orders_bp.post("/checkout")
@jwt_required()
def checkout():

    customer_id = get_current_customer_id()

    try:
        order = OrderService.checkout(
            customer_id
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 400

    return jsonify(
        order_to_dict(order)
    ), 201


@orders_bp.get("")
@jwt_required()
def get_orders():

    customer_id = get_current_customer_id()

    try:
        orders = OrderService.get_orders(
            customer_id
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 404

    return jsonify([
        order_to_dict(order)
        for order in orders
    ])


@orders_bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id: int):

    customer_id = get_current_customer_id()

    try:
        order = OrderService.get_order(
            customer_id=customer_id,
            order_id=order_id,
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 404

    return jsonify(
        order_to_dict(order)
    )