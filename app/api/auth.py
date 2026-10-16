from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from app.auth import create_customer_tokens
from app.services.customer_service import CustomerService
from app.services.password_reset_service import PasswordResetService


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth",
)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body must be JSON"
        }, 400

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
        return {
            "error": str(exc)
        }, 400

    tokens = create_customer_tokens(customer.id)

    return jsonify({
        "message": "Customer registered successfully",
        **tokens,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        },
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body must be JSON"
        }, 400

    email = data.get("email")
    password = data.get("password")

    if email is None or password is None:
        return {
            "error": "Email and password are required"
        }, 400

    customer = CustomerService.authenticate(
        email=str(email),
        password=str(password),
    )

    if customer is None:
        return {
            "error": "Invalid email or password"
        }, 401

    tokens = create_customer_tokens(customer.id)

    return jsonify({
        **tokens,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        },
    })

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token only when a valid refresh token is supplied."""
    claims = get_jwt()
    session_id = claims.get("sid")
    if not session_id:
        return {"error": "Refresh token is missing a session identifier"}, 401

    access_token = create_access_token(
        identity=str(get_jwt_identity()),
        additional_claims={"sid": session_id},
    )
    return jsonify({"access_token": access_token})


@auth_bp.post("/password-reset/request")
def request_password_reset():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("email"), str) or not data["email"].strip():
        return {"error": "Email is required"}, 400

    PasswordResetService.request_reset(data["email"])
    # Do not disclose whether an account with this email exists.
    return jsonify({
        "message": "If an account exists for that email, password-reset instructions will be sent."
    }), 200


@auth_bp.post("/password-reset/confirm")
def confirm_password_reset():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "Request body must be JSON"}, 400

    token = data.get("token")
    new_password = data.get("new_password")
    if not isinstance(token, str) or not token or not isinstance(new_password, str) or not new_password:
        return {"error": "Token and new_password are required"}, 400

    if not PasswordResetService.reset_password(token, new_password):
        return {"error": "Password-reset token is invalid, expired, or already used"}, 400

    return jsonify({"message": "Password has been reset successfully"}), 200
