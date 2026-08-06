import os
import re


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
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
    # Resolved lazily so importing this module in dev doesn't require the env var.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    CORS_ORIGINS = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CORS_ORIGINS = ["http://localhost:5173"]
