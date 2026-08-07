import pytest


@pytest.fixture(autouse=True)
def _auto_login(register_and_login):
    register_and_login()


def test_list_empty(client):
    res = client.get("/api/todos/")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_returns_newest_first(client, make_todo):
    first = make_todo("first")
    second = make_todo("second")

    res = client.get("/api/todos/")
    assert res.status_code == 200
    body = res.get_json()
    assert [t["id"] for t in body] == [second["id"], first["id"]]


def test_create_success(client):
    res = client.post("/api/todos/", json={"title": "  buy milk  "})
    assert res.status_code == 201
    body = res.get_json()
    assert body["title"] == "buy milk"
    assert body["completed"] is False
    assert isinstance(body["id"], int)


def test_create_missing_title(client):
    res = client.post("/api/todos/", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_empty_title(client):
    res = client.post("/api/todos/", json={"title": "   "})
    assert res.status_code == 400


def test_create_no_json_body(client):
    res = client.post("/api/todos/")
    assert res.status_code == 400


def test_get_single(client, make_todo):
    created = make_todo("read me")
    res = client.get(f"/api/todos/{created['id']}")
    assert res.status_code == 200
    assert res.get_json()["title"] == "read me"


def test_get_missing(client):
    res = client.get("/api/todos/999")
    assert res.status_code == 404


def test_patch_title(client, make_todo):
    todo = make_todo("old")
    res = client.patch(f"/api/todos/{todo['id']}", json={"title": "new"})
    assert res.status_code == 200
    assert res.get_json()["title"] == "new"


def test_patch_completed(client, make_todo):
    todo = make_todo()
    res = client.patch(f"/api/todos/{todo['id']}", json={"completed": True})
    assert res.status_code == 200
    assert res.get_json()["completed"] is True


def test_patch_partial_keeps_other_fields(client, make_todo):
    todo = make_todo("keep me")
    res = client.patch(f"/api/todos/{todo['id']}", json={"completed": True})
    assert res.status_code == 200
    body = res.get_json()
    assert body["title"] == "keep me"
    assert body["completed"] is True


def test_patch_rejects_empty_title(client, make_todo):
    todo = make_todo()
    res = client.patch(f"/api/todos/{todo['id']}", json={"title": "  "})
    assert res.status_code == 400


def test_patch_rejects_non_bool_completed(client, make_todo):
    todo = make_todo()
    res = client.patch(f"/api/todos/{todo['id']}", json={"completed": "yes"})
    assert res.status_code == 400


def test_patch_missing(client):
    res = client.patch("/api/todos/999", json={"title": "x"})
    assert res.status_code == 404


def test_delete_success(client, make_todo):
    todo = make_todo()
    res = client.delete(f"/api/todos/{todo['id']}")
    assert res.status_code == 204
    assert res.data == b""

    follow = client.get(f"/api/todos/{todo['id']}")
    assert follow.status_code == 404


def test_delete_missing(client):
    res = client.delete("/api/todos/999")
    assert res.status_code == 404
