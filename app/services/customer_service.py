from datetime import datetime, timedelta, timezone

from flask import current_app

from app import db
from app.models import Customer


def _utcnow_naive() -> datetime:
    """Return UTC now as a naive datetime, matching SQLite DateTime storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CustomerService:

    @staticmethod
    def create_customer(
        name: str,
        email: str,
        password: str,
    ) -> Customer:

        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError(
                "Customer name cannot be empty"
            )

        if not email:
            raise ValueError(
                "Customer email cannot be empty"
            )

        if not password:
            raise ValueError(
                "Customer password cannot be empty"
            )

        existing = db.session.scalar(
            db.select(Customer).where(
                Customer.email == email
            )
        )

        if existing is not None:
            raise ValueError(
                "Customer email already exists"
            )

        customer = Customer(
            name=name,
            email=email,
        )

        customer.set_password(password)

        db.session.add(customer)
        db.session.commit()

        return customer

    @staticmethod
    def authenticate(
        email: str,
        password: str,
    ) -> Customer | None:

        email = email.strip().lower()

        customer = db.session.scalar(
            db.select(Customer).where(
                Customer.email == email
            )
        )

        # Keep the response generic for unknown, incorrect and locked accounts.
        if customer is None:
            return None

        now = _utcnow_naive()
        if customer.locked_until is not None:
            if customer.locked_until > now:
                return None

            # Lockout has elapsed; allow a fresh sequence of attempts.
            customer.failed_login_attempts = 0
            customer.locked_until = None

        if not customer.check_password(password):
            customer.failed_login_attempts += 1
            max_attempts = int(
                current_app.config.get("MAX_FAILED_LOGIN_ATTEMPTS", 5)
            )
            if customer.failed_login_attempts >= max_attempts:
                lockout_minutes = int(
                    current_app.config.get("ACCOUNT_LOCKOUT_DURATION_MINUTES", 15)
                )
                customer.locked_until = now + timedelta(minutes=lockout_minutes)
            db.session.commit()
            return None

        customer.failed_login_attempts = 0
        customer.locked_until = None
        db.session.commit()
        return customer

    @staticmethod
    def get_customers() -> list[Customer]:

        return db.session.scalars(
            db.select(Customer).order_by(Customer.id)
        ).all()

    @staticmethod
    def get_customer(
        customer_id: int,
    ) -> Customer | None:

        return db.session.get(
            Customer,
            customer_id,
        )