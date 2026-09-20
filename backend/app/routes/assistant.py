from flask import Blueprint, jsonify, request

from ..auth import login_required
from ..services.ollama import AssistantUnavailable, suggest_step

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.post("/next-step")
@login_required
def next_step():
    if request.content_length and request.content_length > 8192:
        return jsonify({"error": "Request is too large."}), 413
    data = request.get_json(silent=True)
    task = data.get("task") if isinstance(data, dict) else None
    if not isinstance(task, str) or not 1 <= len(task.strip()) <= 1000:
        return jsonify({"error": "Describe your task in 1–1000 characters."}), 400
    try:
        step = suggest_step(task.strip())
    except AssistantUnavailable as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify({"step": step})
