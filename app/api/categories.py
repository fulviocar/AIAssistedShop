from flask import Blueprint, jsonify, request

from app.services.category_service import CategoryService


categories_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/api/categories",
)


def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
    }


@categories_bp.post("")
def create_category():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body must be JSON"}, 400

    if "name" not in data:
        return {"error": "Missing required field: name"}, 400

    try:
        category = CategoryService.create_category(
            str(data["name"])
        )
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return jsonify(category_to_dict(category)), 201


@categories_bp.get("")
def get_categories():
    categories = CategoryService.get_categories()

    return jsonify([
        category_to_dict(category)
        for category in categories
    ])


@categories_bp.get("/<int:category_id>")
def get_category(category_id: int):
    category = CategoryService.get_category(category_id)

    if category is None:
        return {"error": "Category not found"}, 404

    return jsonify(category_to_dict(category))