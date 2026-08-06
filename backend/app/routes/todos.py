from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Todo

todos_bp = Blueprint("todos", __name__)


@todos_bp.get("/")
def list_todos():
    """GET /api/todos -> 200 [Todo]

    Returns all todos ordered by newest first.
    """
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([t.to_dict() for t in todos]), 200


@todos_bp.post("/")
def create_todo():
    """POST /api/todos { title: str } -> 201 Todo | 400"""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    todo = Todo(title=title); db.session.add(todo); db.session.commit()
    return jsonify(todo.to_dict()), 201


@todos_bp.get("/<int:todo_id>")
def get_todo(todo_id: int):
    """GET /api/todos/<id> -> 200 Todo | 404"""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(todo.to_dict()), 200


@todos_bp.patch("/<int:todo_id>")
def update_todo(todo_id: int):
    """PATCH /api/todos/<id> { title?: str, completed?: bool } -> 200 Todo | 400 | 404"""
    # Fetch todo with db.session.get(Todo, todo_id); 404 if missing.
    todo = db.session.get(Todo, todo_id)
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
    db.session.commit()
    return jsonify(todo.to_dict()), 200


@todos_bp.delete("/<int:todo_id>")
def delete_todo(todo_id: int):
    """DELETE /api/todos/<id> -> 204 | 404"""
    # Fetch todo with db.session.get(Todo, todo_id); 404 if missing.
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "not found"}), 404
    # Delete the todo and commit the session.    
    db.session.delete(todo)
    db.session.commit()
    return "", 204
