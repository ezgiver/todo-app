"""Integration tests for the auth API (register, login, logout, me)."""


class TestRegister:
    def test_register_returns_user(self, api, unique_email, test_password):
        res = api.post("/api/auth/register", json={
            "email": unique_email,
            "password": test_password,
            "display_name": "New User",
        })
        assert res.status_code == 201
        body = res.json()
        assert body["email"] == unique_email
        assert body["display_name"] == "New User"
        assert "password" not in body
        assert "password_hash" not in body

    def test_register_rejects_duplicate_email(self, api, registered_user, unique_email, test_password):
        res = api.post("/api/auth/register", json={
            "email": unique_email,
            "password": test_password,
            "display_name": "Duplicate",
        })
        assert res.status_code == 400

    def test_register_rejects_invalid_email(self, api, test_password):
        res = api.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": test_password,
            "display_name": "Bad Email",
        })
        assert res.status_code == 400

    def test_register_rejects_short_password(self, api, unique_email):
        res = api.post("/api/auth/register", json={
            "email": unique_email,
            "password": "short",
            "display_name": "Short Pass",
        })
        assert res.status_code == 400


class TestLogin:
    def test_login_success(self, api, registered_user, unique_email, test_password):
        res = api.post("/api/auth/login", json={
            "email": unique_email,
            "password": test_password,
        })
        assert res.status_code == 200
        body = res.json()
        assert body["email"] == unique_email

    def test_login_wrong_password(self, api, registered_user, unique_email):
        res = api.post("/api/auth/login", json={
            "email": unique_email,
            "password": "wrong-password-here",
        })
        assert res.status_code == 401
        assert res.json() == {"error": "invalid credentials"}

    def test_login_unknown_email(self, api):
        res = api.post("/api/auth/login", json={
            "email": "ghost@nowhere.com",
            "password": "doesntmatter123",
        })
        assert res.status_code == 401


class TestMe:
    def test_me_authenticated(self, authenticated_api, unique_email):
        res = authenticated_api.get("/api/auth/me")
        assert res.status_code == 200
        assert res.json()["email"] == unique_email

    def test_me_unauthenticated(self, api):
        res = api.get("/api/auth/me")
        assert res.status_code == 401


class TestLogout:
    def test_logout_clears_session(self, authenticated_api):
        res = authenticated_api.post("/api/auth/logout")
        assert res.status_code == 204

        # Session should be gone now
        me = authenticated_api.get("/api/auth/me")
        assert me.status_code == 401
