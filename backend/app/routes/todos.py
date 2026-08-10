from datetime import datetime

from flask import Blueprint, jsonify, request

from ..auth import current_user_id, login_required
from ..extensions import db
from ..models import Todo

todos_bp = Blueprint("todos", __name__)


def _find_owned_todo(todo_id: int) -> Todo | None:
    return Todo.query.filter_by(id=todo_id, user_id=current_user_id()).first()


def _parse_due_at(raw_due_at):
    if raw_due_at in (None, ""):
        return None
    if not isinstance(raw_due_at, str):
        return None
    try:
        return datetime.fromisoformat(raw_due_at)
    except ValueError:
        return None


@todos_bp.get("/")
@login_required
def list_todos():
    todos = (
        Todo.query.filter_by(user_id=current_user_id())
        .order_by(Todo.created_at.desc(), Todo.id.desc())
        .all()
    )
    return jsonify([t.to_dict() for t in todos]), 200


@todos_bp.post("/")
@login_required
def create_todo():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    due_at = _parse_due_at(data.get("due_at"))
    if data.get("due_at") not in (None, "") and due_at is None:
        return jsonify({"error": "due_at must be an ISO datetime string"}), 400
    todo = Todo(title=title, user_id=current_user_id(), due_at=due_at)
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@todos_bp.get("/<int:todo_id>")
@login_required
def get_todo(todo_id: int):
    todo = _find_owned_todo(todo_id)
    if todo is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(todo.to_dict()), 200


@todos_bp.patch("/<int:todo_id>")
@login_required
def update_todo(todo_id: int):
    todo = _find_owned_todo(todo_id)
    if todo is None:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title is required"}), 400
        todo.title = title
    if "completed" in data:
        completed = data.get("completed")
        if not isinstance(completed, bool):
            return jsonify({"error": "completed must be a boolean"}), 400
        todo.completed = completed
    if "due_at" in data:
        due_at = _parse_due_at(data.get("due_at"))
        if data.get("due_at") not in (None, "") and due_at is None:
            return jsonify({"error": "due_at must be an ISO datetime string"}), 400
        todo.due_at = due_at
    db.session.commit()
    return jsonify(todo.to_dict()), 200


@todos_bp.delete("/<int:todo_id>")
@login_required
def delete_todo(todo_id: int):
    todo = _find_owned_todo(todo_id)
    if todo is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return "", 204
