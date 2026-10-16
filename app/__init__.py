from datetime import datetime, timedelta, timezone

from flask import Flask, current_app, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
jwt = JWTManager()


def create_app(config=None) -> Flask:

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///aiassistedshop.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = (
        "change-this-development-secret"
    )

    app.config.setdefault("SESSION_INACTIVITY_TIMEOUT_MINUTES", 15)
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=8))
    app.config.setdefault("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))
    app.config.setdefault("PASSWORD_RESET_TOKEN_EXPIRES", timedelta(hours=1))
    app.config.setdefault("PASSWORD_RESET_URL_BASE", "http://localhost:5000/reset-password?token=")
    app.config.setdefault("PASSWORD_RESET_EMAIL_SENDER", None)
    app.config.setdefault("PASSWORD_RESET_LOG_LINKS", True)
    app.config.setdefault("MAX_FAILED_LOGIN_ATTEMPTS", 5)
    app.config.setdefault("ACCOUNT_LOCKOUT_DURATION_MINUTES", 15)

    if config:
        app.config.update(config)

    db.init_app(app)
    jwt.init_app(app)

    from app.models import (
        Cart,
        CartItem,
        Category,
        Customer,
        AuthSession,
        PasswordResetToken,
        Order,
        OrderItem,
        Product,
    )

    @jwt.token_in_blocklist_loader
    def check_session_inactivity(jwt_header, jwt_payload):
        session_id = jwt_payload.get("sid")
        if not session_id:
            return True

        auth_session = db.session.get(AuthSession, session_id)
        if auth_session is None:
            return True

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        timeout = timedelta(
            minutes=current_app.config["SESSION_INACTIVITY_TIMEOUT_MINUTES"]
        )

        if now - auth_session.last_activity_at >= timeout:
            db.session.delete(auth_session)
            db.session.commit()
            return True

        auth_session.last_activity_at = now
        db.session.commit()
        return False

    from app.api.categories import categories_bp
    from app.api.customers import customers_bp
    from app.api.products import products_bp
    from app.api.cart import cart_bp
    from app.api.orders import orders_bp
    from app.api.auth import auth_bp

    app.register_blueprint(categories_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)
    
    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/reset-password")
    def reset_password_page():
        from flask import request
        return render_template("reset_password.html", token=request.args.get("token", ""))

    return app