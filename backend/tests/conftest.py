import pytest

from app import create_app
from app.extensions import db


DEFAULT_PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def app():
    app = create_app("config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def register_and_login(client):
    """Register a user and log them in on the shared client."""

    def _do(
        email: str = "alice@example.com",
        password: str = DEFAULT_PASSWORD,
        display_name: str = "Alice",
    ):
        r = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "display_name": display_name,
            },
        )
        assert r.status_code == 201, r.get_json()
        # Register no longer auto-logs-in; call login explicitly.
        l = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert l.status_code == 200, l.get_json()
        return l.get_json()

    return _do


@pytest.fixture
def make_todo(client):
    """POST a todo and return it. Caller is responsible for logging in first."""

    def _make(title: str = "Sample"):
        res = client.post("/api/todos/", json={"title": title})
        assert res.status_code == 201, res.get_json()
        return res.get_json()

    return _make
