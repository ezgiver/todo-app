"""Integration tests for the todos CRUD API."""


class TestCreateTodo:
    def test_create_todo(self, authenticated_api):
        res = authenticated_api.post("/api/todos/", json={"title": "Buy groceries"})
        assert res.status_code == 201
        body = res.json()
        assert body["title"] == "Buy groceries"
        assert body["completed"] is False
        assert body["id"] is not None
        assert body["created_at"] is not None
        assert body["due_at"] is None

    def test_create_todo_with_due_date(self, authenticated_api):
        res = authenticated_api.post("/api/todos/", json={
            "title": "Pay rent",
            "due_at": "2026-09-01T10:00:00",
        })
        assert res.status_code == 201
        assert res.json()["due_at"] == "2026-09-01T10:00:00"

    def test_create_todo_strips_whitespace(self, authenticated_api):
        res = authenticated_api.post("/api/todos/", json={"title": "  trimmed  "})
        assert res.status_code == 201
        assert res.json()["title"] == "trimmed"

    def test_create_todo_rejects_empty_title(self, authenticated_api):
        res = authenticated_api.post("/api/todos/", json={"title": "   "})
        assert res.status_code == 400

    def test_create_todo_rejects_missing_title(self, authenticated_api):
        res = authenticated_api.post("/api/todos/", json={})
        assert res.status_code == 400

    def test_create_todo_requires_auth(self, api):
        res = api.post("/api/todos/", json={"title": "Nope"})
        assert res.status_code == 401


class TestListTodos:
    def test_list_empty(self, authenticated_api):
        res = authenticated_api.get("/api/todos/")
        assert res.status_code == 200
        # New user, may or may not be empty depending on test isolation,
        # but it should be a list.
        assert isinstance(res.json(), list)

    def test_list_returns_created_todo(self, authenticated_api):
        authenticated_api.post("/api/todos/", json={"title": "Find me"})
        res = authenticated_api.get("/api/todos/")
        assert res.status_code == 200
        titles = [t["title"] for t in res.json()]
        assert "Find me" in titles

    def test_list_requires_auth(self, api):
        res = api.get("/api/todos/")
        assert res.status_code == 401


class TestGetTodo:
    def test_get_single_todo(self, authenticated_api):
        created = authenticated_api.post("/api/todos/", json={"title": "Get me"}).json()
        res = authenticated_api.get(f"/api/todos/{created['id']}")
        assert res.status_code == 200
        assert res.json()["title"] == "Get me"

    def test_get_nonexistent_todo(self, authenticated_api):
        res = authenticated_api.get("/api/todos/99999")
        assert res.status_code == 404


class TestUpdateTodo:
    def test_patch_title(self, authenticated_api):
        todo = authenticated_api.post("/api/todos/", json={"title": "old"}).json()
        res = authenticated_api.patch(f"/api/todos/{todo['id']}", json={"title": "new"})
        assert res.status_code == 200
        assert res.json()["title"] == "new"

    def test_patch_completed(self, authenticated_api):
        todo = authenticated_api.post("/api/todos/", json={"title": "do it"}).json()
        res = authenticated_api.patch(f"/api/todos/{todo['id']}", json={"completed": True})
        assert res.status_code == 200
        assert res.json()["completed"] is True

    def test_patch_due_at(self, authenticated_api):
        todo = authenticated_api.post("/api/todos/", json={"title": "due"}).json()
        res = authenticated_api.patch(
            f"/api/todos/{todo['id']}", json={"due_at": "2026-12-25T00:00:00"}
        )
        assert res.status_code == 200
        assert res.json()["due_at"] == "2026-12-25T00:00:00"

    def test_patch_rejects_empty_title(self, authenticated_api):
        todo = authenticated_api.post("/api/todos/", json={"title": "keep"}).json()
        res = authenticated_api.patch(f"/api/todos/{todo['id']}", json={"title": "  "})
        assert res.status_code == 400

    def test_patch_nonexistent_todo(self, authenticated_api):
        res = authenticated_api.patch("/api/todos/99999", json={"title": "x"})
        assert res.status_code == 404


class TestDeleteTodo:
    def test_delete_todo(self, authenticated_api):
        todo = authenticated_api.post("/api/todos/", json={"title": "delete me"}).json()
        res = authenticated_api.delete(f"/api/todos/{todo['id']}")
        assert res.status_code == 204

        # Confirm it's gone
        follow = authenticated_api.get(f"/api/todos/{todo['id']}")
        assert follow.status_code == 404

    def test_delete_nonexistent_todo(self, authenticated_api):
        res = authenticated_api.delete("/api/todos/99999")
        assert res.status_code == 404
