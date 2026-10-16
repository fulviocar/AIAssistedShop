from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.customer_service import CustomerService


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers",
)


def customer_to_dict(customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "created_at": customer.created_at.isoformat(),
    }


@customers_bp.post("")
def create_customer():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body must be JSON"}, 400

    required_fields = {
        "name",
        "email",
        "password",
    }

    missing_fields = required_fields - data.keys()

    if missing_fields:
        return {
            "error": "Missing required fields",
            "fields": sorted(missing_fields),
        }, 400

    try:
        customer = CustomerService.create_customer(
            name=str(data["name"]),
            email=str(data["email"]),
            password=str(data["password"]),
        )
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return jsonify(customer_to_dict(customer)), 201


@customers_bp.get("")
def get_customers():
    customers = CustomerService.get_customers()

    return jsonify([
        customer_to_dict(customer)
        for customer in customers
    ])


@customers_bp.get("/<int:customer_id>")
def get_customer(customer_id: int):
    customer = CustomerService.get_customer(customer_id)

    if customer is None:
        return {"error": "Customer not found"}, 404

    return jsonify(customer_to_dict(customer))


@customers_bp.get("/me")
@jwt_required()
def get_current_customer():
    customer_id = int(get_jwt_identity())

    customer = CustomerService.get_customer(customer_id)

    if customer is None:
        return {"error": "Customer not found"}, 404

    return jsonify(customer_to_dict(customer))