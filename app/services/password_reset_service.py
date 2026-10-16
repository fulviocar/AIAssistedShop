from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from urllib.parse import quote

from flask import current_app

from app import db
from app.models import Customer, PasswordResetToken


def _utcnow_naive() -> datetime:
    """Return UTC now as a naive datetime to match SQLite DateTime storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class PasswordResetService:
    @staticmethod
    def request_reset(email: str) -> None:
        email = email.strip().lower()
        customer = db.session.scalar(
            db.select(Customer).where(Customer.email == email)
        )
        if customer is None:
            return

        now = _utcnow_naive()
        # Invalidate any outstanding reset links when a newer one is requested.
        outstanding = db.session.scalars(
            db.select(PasswordResetToken).where(
                PasswordResetToken.customer_id == customer.id,
                PasswordResetToken.used_at.is_(None),
            )
        ).all()
        for reset_record in outstanding:
            reset_record.used_at = now

        raw_token = secrets.token_urlsafe(32)
        lifetime = current_app.config.get(
            "PASSWORD_RESET_TOKEN_EXPIRES", timedelta(hours=1)
        )
        if isinstance(lifetime, (int, float)):
            lifetime = timedelta(seconds=lifetime)

        reset_record = PasswordResetToken(
            customer_id=customer.id,
            token_hash=_hash_token(raw_token),
            created_at=now,
            expires_at=now + lifetime,
        )
        db.session.add(reset_record)
        db.session.commit()

        base_url = current_app.config.get(
            "PASSWORD_RESET_URL_BASE",
            "http://localhost:5000/reset-password?token=",
        )
        reset_url = f"{base_url}{quote(raw_token)}"
        sender = current_app.config.get("PASSWORD_RESET_EMAIL_SENDER")
        if callable(sender):
            sender(customer.email, reset_url)
        elif current_app.config.get("PASSWORD_RESET_LOG_LINKS", False):
            current_app.logger.warning(
                "Password reset link for %s: %s", customer.email, reset_url
            )

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        if not token or not new_password:
            return False

        now = _utcnow_naive()
        reset_record = db.session.scalar(
            db.select(PasswordResetToken).where(
                PasswordResetToken.token_hash == _hash_token(token)
            )
        )
        if reset_record is None or reset_record.used_at is not None:
            return False
        if reset_record.expires_at <= now:
            return False

        customer = db.session.get(Customer, reset_record.customer_id)
        if customer is None:
            return False

        customer.set_password(new_password)
        reset_record.used_at = now

        # Revoke outstanding reset tokens for this account after a successful reset.
        other_tokens = db.session.scalars(
            db.select(PasswordResetToken).where(
                PasswordResetToken.customer_id == customer.id,
                PasswordResetToken.id != reset_record.id,
                PasswordResetToken.used_at.is_(None),
            )
        ).all()
        for other_token in other_tokens:
            other_token.used_at = now

        # Revoke existing login sessions so the password change takes effect promptly.
        from app.models import AuthSession
        sessions = db.session.scalars(
            db.select(AuthSession).where(AuthSession.customer_id == customer.id)
        ).all()
        for session in sessions:
            db.session.delete(session)

        db.session.commit()
        return True
