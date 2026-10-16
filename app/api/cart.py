from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.cart_service import CartService


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/api/customers/me/cart",
)


def get_current_customer_id() -> int:
    return int(get_jwt_identity())


def cart_to_dict(cart):
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": str(item.product.price),
                "subtotal": str(
                    item.product.price * item.quantity
                ),
            }
            for item in cart.items
        ],
        "total": str(
            CartService.calculate_total(cart)
        ),
    }


@cart_bp.get("")
@jwt_required()
def get_cart():

    customer_id = get_current_customer_id()

    try:
        cart = CartService.get_cart(customer_id)
    except ValueError as exc:
        return {"error": str(exc)}, 404

    return jsonify(cart_to_dict(cart))


@cart_bp.post("/items")
@jwt_required()
def add_item():

    customer_id = get_current_customer_id()

    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body must be JSON"
        }, 400

    if "product_id" not in data:
        return {
            "error": "Missing required field: product_id"
        }, 400

    if "quantity" not in data:
        return {
            "error": "Missing required field: quantity"
        }, 400

    try:
        product_id = int(data["product_id"])
        quantity = int(data["quantity"])
    except (TypeError, ValueError):
        return {
            "error": "product_id and quantity must be integers"
        }, 400

    try:
        item = CartService.add_item(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 400

    return jsonify({
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
    }), 201


@cart_bp.put("/items/<int:item_id>")
@jwt_required()
def update_item(item_id: int):

    customer_id = get_current_customer_id()

    data = request.get_json(silent=True)

    if not data or "quantity" not in data:
        return {
            "error": "Missing required field: quantity"
        }, 400

    try:
        quantity = int(data["quantity"])
    except (TypeError, ValueError):
        return {
            "error": "Quantity must be an integer"
        }, 400

    try:
        item = CartService.update_item(
            customer_id=customer_id,
            item_id=item_id,
            quantity=quantity,
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 400

    return jsonify({
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
    })


@cart_bp.delete("/items/<int:item_id>")
@jwt_required()
def remove_item(item_id: int):

    customer_id = get_current_customer_id()

    try:
        CartService.remove_item(
            customer_id=customer_id,
            item_id=item_id,
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 404

    return "", 204


@cart_bp.delete("")
@jwt_required()
def clear_cart():

    customer_id = get_current_customer_id()

    try:
        CartService.clear_cart(customer_id)
    except ValueError as exc:
        return {
            "error": str(exc)
        }, 404

    return "", 204