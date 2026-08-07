import os
import re
from datetime import timedelta


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-for-prod")
    SESSION_COOKIE_SECURE = False   # local HTTP
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///todo.db"
    )
    # Dev: allow any localhost/127.0.0.1 port. Override CORS_ORIGINS env for prod.
    _origins_env = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]
    CORS_ORIGINS = _origins_env or [
        re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")
    ]


class ProductionConfig(BaseConfig):
    DEBUG = False
    # SECRET_KEY validated at app startup (create_app); no default here.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_SECURE = True
    # Resolved lazily so importing this module in dev doesn't require the env var.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    CORS_ORIGINS = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret"
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CORS_ORIGINS = ["http://localhost:5173"]
