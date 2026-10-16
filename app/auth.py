from datetime import datetime, timezone
from uuid import uuid4

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)

from app import db
from app.models import AuthSession


def utcnow_naive() -> datetime:
    """Return the current UTC time as a naive datetime for SQLite storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_customer_access_token(customer_id: int) -> str:
    """Create an access token linked to a persistent server-side session."""
    session_id = uuid4().hex
    now = utcnow_naive()
    auth_session = AuthSession(
        id=session_id,
        customer_id=int(customer_id),
        created_at=now,
        last_activity_at=now,
    )
    db.session.add(auth_session)
    db.session.commit()

    return create_access_token(
        identity=str(customer_id),
        additional_claims={"sid": session_id},
    )


def get_current_customer_id() -> int:
    return int(get_jwt_identity())


def create_customer_tokens(customer_id: int) -> dict[str, str]:
    """Create access and refresh tokens associated with one server-side session."""
    session_id = uuid4().hex
    now = utcnow_naive()
    auth_session = AuthSession(
        id=session_id,
        customer_id=int(customer_id),
        created_at=now,
        last_activity_at=now,
    )
    db.session.add(auth_session)
    db.session.commit()

    identity = str(customer_id)
    claims = {"sid": session_id}
    return {
        "access_token": create_access_token(
            identity=identity,
            additional_claims=claims,
        ),
        "refresh_token": create_refresh_token(
            identity=identity,
            additional_claims=claims,
        ),
    }
