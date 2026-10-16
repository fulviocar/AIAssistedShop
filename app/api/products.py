from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from app.services.product_service import ProductService


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products",
)


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
    }


@products_bp.post("")
def create_product():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body must be JSON"}, 400

    required_fields = {
        "name",
        "description",
        "price",
        "stock_quantity",
        "category_id",
    }

    missing_fields = required_fields - data.keys()

    if missing_fields:
        return {
            "error": "Missing required fields",
            "fields": sorted(missing_fields),
        }, 400

    try:
        price = Decimal(str(data["price"]))
    except (InvalidOperation, TypeError, ValueError):
        return {"error": "Invalid price"}, 400

    try:
        stock_quantity = int(data["stock_quantity"])
        category_id = int(data["category_id"])
    except (TypeError, ValueError):
        return {
            "error": "stock_quantity and category_id must be integers"
        }, 400

    try:
        product = ProductService.create_product(
            name=str(data["name"]),
            description=str(data["description"]),
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id,
        )
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return jsonify(product_to_dict(product)), 201


@products_bp.get("")
def get_products():

    search = request.args.get(
        "search",
        default="",
        type=str,
    )

    products = ProductService.get_products(
        search=search
    )

    return jsonify([
        product_to_dict(product)
        for product in products
    ])


@products_bp.get("/<int:product_id>")
def get_product(product_id: int):
    product = ProductService.get_product(product_id)

    if product is None:
        return {"error": "Product not found"}, 404

    return jsonify(product_to_dict(product))