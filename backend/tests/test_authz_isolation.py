from tests.conftest import DEFAULT_PASSWORD


def _register_and_login(client, email, display_name):
    r = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": DEFAULT_PASSWORD,
            "display_name": display_name,
        },
    )
    assert r.status_code == 201, r.get_json()
    l = client.post(
        "/api/auth/login", json={"email": email, "password": DEFAULT_PASSWORD}
    )
    assert l.status_code == 200, l.get_json()


def test_users_cannot_see_each_others_todos(app):
    alice = app.test_client()
    bob = app.test_client()

    _register_and_login(alice, "alice@example.com", "Alice")
    _register_and_login(bob, "bob@example.com", "Bob")

    alice_todo = alice.post("/api/todos/", json={"title": "alice-secret"}).get_json()

    bob_list = bob.get("/api/todos/").get_json()
    assert bob_list == []

    # Direct access to Alice's todo id must 404 for Bob.
    assert bob.get(f"/api/todos/{alice_todo['id']}").status_code == 404
    assert bob.patch(
        f"/api/todos/{alice_todo['id']}", json={"completed": True}
    ).status_code == 404
    assert bob.delete(f"/api/todos/{alice_todo['id']}").status_code == 404

    # Alice can still see her own todo untouched.
    still_there = alice.get(f"/api/todos/{alice_todo['id']}").get_json()
    assert still_there["title"] == "alice-secret"
    assert still_there["completed"] is False
