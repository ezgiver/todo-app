from flask import Blueprint, jsonify, request

from ..auth import login_required
from ..services.ollama import AssistantUnavailable, suggest_step, suggest_steps

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


@assistant_bp.post("/steps")
@login_required
def steps():
    if request.content_length and request.content_length > 8192:
        return jsonify({"error": "Request is too large."}), 413
    data = request.get_json(silent=True)
    task = data.get("task") if isinstance(data, dict) else None
    if not isinstance(task, str) or not 1 <= len(task.strip()) <= 1000:
        return jsonify({"error": "Describe your task in 1–1000 characters."}), 400
    blocker = data.get("blocker", "")
    minutes = data.get("available_minutes")
    if not isinstance(blocker, str) or len(blocker.strip()) > 1000:
        return jsonify({"error": "Blocker must be text up to 1000 characters."}), 400
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= 120):
        return jsonify({"error": "Available time must be a whole number from 1 to 120 minutes."}), 400
    try:
        return jsonify(suggest_steps(task.strip(), blocker.strip(), minutes))
    except AssistantUnavailable as exc:
        return jsonify({"error": str(exc)}), 503
