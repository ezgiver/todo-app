import pytest

from app import create_app
from app.extensions import db


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
def make_todo(client):
    """Helper: POST a todo and return the parsed JSON body."""

    def _make(title: str = "Sample"):
        res = client.post("/api/todos/", json={"title": title})
        assert res.status_code == 201, res.get_json()
        return res.get_json()

    return _make
