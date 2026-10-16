from datetime import timedelta


class Config:
    TESTING = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    PASSWORD_RESET_TOKEN_EXPIRES = timedelta(hours=1)
    PASSWORD_RESET_URL_BASE = "http://localhost:5000/reset-password?token="
    PASSWORD_RESET_EMAIL_SENDER = None
    PASSWORD_RESET_LOG_LINKS = True
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 15


class TestConfig(Config):
    TESTING = True
