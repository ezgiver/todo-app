import os
import uuid

import httpx
import pytest


BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")


def _server_is_reachable() -> bool:
    """Check if the server is running before we attempt any tests."""
    try:
        r = httpx.get(f"{BASE_URL}/api/health", timeout=3)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


# Skip the entire integration suite if no server is reachable.
pytestmark = pytest.mark.skipif(
    not _server_is_reachable(),
    reason=f"Integration server not reachable at {BASE_URL}",
)


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API requests."""
    return BASE_URL


@pytest.fixture()
def api():
    """A fresh httpx client with cookie persistence (like a browser session)."""
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        yield client


@pytest.fixture()
def unique_email():
    """Generate a unique email so tests don't collide with each other."""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture()
def test_password():
    return "integration-test-pass-123"


@pytest.fixture()
def registered_user(api, unique_email, test_password):
    """Register a user and return their info. Does NOT log in."""
    res = api.post("/api/auth/register", json={
        "email": unique_email,
        "password": test_password,
        "display_name": "Integration Tester",
    })
    assert res.status_code == 201, res.text
    return res.json()


@pytest.fixture()
def authenticated_api(api, registered_user, unique_email, test_password):
    """An API client that is already logged in."""
    res = api.post("/api/auth/login", json={
        "email": unique_email,
        "password": test_password,
    })
    assert res.status_code == 200, res.text
    return api
