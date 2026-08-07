import json

from tests.conftest import DEFAULT_PASSWORD


def _register(client, **overrides):
    payload = {
        "email": "alice@example.com",
        "password": DEFAULT_PASSWORD,
        "display_name": "Alice",
        **overrides,
    }
    return client.post("/api/auth/register", json=payload)


def test_register_success_returns_user_but_does_not_log_in(client):
    res = _register(client)
    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert "password" not in body and "password_hash" not in body

    # Register does NOT create a session — /me must fail until login.
    assert client.get("/api/auth/me").status_code == 401


def test_register_lowercases_email(client):
    res = _register(client, email="Alice@Example.COM")
    assert res.status_code == 201
    assert res.get_json()["email"] == "alice@example.com"


def test_register_rejects_invalid_email(client):
    assert _register(client, email="not-an-email").status_code == 400


def test_register_rejects_short_password(client):
    assert _register(client, password="short").status_code == 400


def test_register_rejects_password_equal_to_email(client):
    email = "veryuniqueemail@example.com"
    assert _register(client, email=email, password=email).status_code == 400


def test_register_rejects_missing_display_name(client):
    assert _register(client, display_name="").status_code == 400


def test_register_duplicate_returns_generic_error(client):
    assert _register(client).status_code == 201
    res = _register(client)
    assert res.status_code == 400
    text = json.dumps(res.get_json()).lower()
    assert "already" not in text and "exists" not in text


def test_login_success(client, register_and_login):
    register_and_login(email="alice@example.com")
    client.post("/api/auth/logout")

    res = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": DEFAULT_PASSWORD},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"


def test_login_wrong_password_generic_error(client, register_and_login):
    register_and_login(email="a@b.com")
    client.post("/api/auth/logout")

    res = client.post(
        "/api/auth/login", json={"email": "a@b.com", "password": "wrongwrongwrong!"}
    )
    assert res.status_code == 401
    assert res.get_json() == {"error": "invalid credentials"}


def test_login_unknown_email_same_error_as_wrong_password(client):
    res = client.post(
        "/api/auth/login", json={"email": "ghost@x.com", "password": "whateverwhat"}
    )
    assert res.status_code == 401
    assert res.get_json() == {"error": "invalid credentials"}


def test_login_missing_fields(client):
    assert client.post("/api/auth/login", json={}).status_code == 401


def test_logout_clears_session(client, register_and_login):
    register_and_login()
    assert client.get("/api/auth/me").status_code == 200

    res = client.post("/api/auth/logout")
    assert res.status_code == 204
    assert res.data == b""
    assert client.get("/api/auth/me").status_code == 401


def test_me_unauthenticated(client):
    assert client.get("/api/auth/me").status_code == 401


def test_todos_require_authentication(client):
    for method, path in [
        ("get", "/api/todos/"),
        ("post", "/api/todos/"),
        ("get", "/api/todos/1"),
        ("patch", "/api/todos/1"),
        ("delete", "/api/todos/1"),
    ]:
        res = getattr(client, method)(path, json={"title": "x"})
        assert res.status_code == 401, f"{method.upper()} {path} allowed unauth"
