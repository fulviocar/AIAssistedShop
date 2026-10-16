# AIAssistedShop

A sample e-commerce application written in Python.

The project is designed as a playground for AI-assisted software development
and testing using Claude Code and Codex.

## Planned architecture

- Python
- Flask Web API
- Web frontend
- PostgreSQL
- SQLAlchemy
- Docker
- pytest
- Playwright
- CI/CD

## Planned functionality

- Customers
- Authentication
- Products
- Categories
- Shopping cart
- Orders
- Checkout
- Inventory
- Customer addresses
- Administration

## Running the application

Create and activate a virtual environment:

```bash
python -m venv .venv

## Password reset (Step 4)

The API supports one-hour, single-use password-reset tokens:

- `POST /api/auth/password-reset/request` with `{"email": "customer@example.com"}`
- `POST /api/auth/password-reset/confirm` with `{"token": "...", "new_password": "..."}`

Reset tokens are generated using a cryptographically secure random source; only a SHA-256 hash is stored in SQLite. A successful reset invalidates the token and revokes the customer's active authentication sessions. Request responses do not reveal whether the email address is registered. Requesting a new reset invalidates older unused reset tokens.

For local development, the reset link is written to the Flask application log by default. Configure `PASSWORD_RESET_EMAIL_SENDER` with a callable accepting `(email, reset_url)` to connect an email provider. In production, disable `PASSWORD_RESET_LOG_LINKS` and configure a real email sender. Set `PASSWORD_RESET_URL_BASE` to the password-reset page in the frontend. The frontend page/email delivery integration is deployment-specific; the reset confirmation endpoint is implemented by the API.

The new `password_reset_tokens` table is created by the application's existing `db.create_all()` initialization, so no ALTER TABLE migration is required for existing databases. Back up your database before deploying changes, as usual.
