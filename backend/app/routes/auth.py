from flask import Blueprint, jsonify, request, session

from ..auth import (
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    is_valid_display_name,
    is_valid_email,
    is_valid_password,
    login_required,
)
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)

# Generic errors — do not leak whether an email exists.
INVALID_CREDENTIALS = ({"error": "invalid credentials"}, 401)
UNABLE_TO_REGISTER = ({"error": "unable to register with those credentials"}, 400)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    display_name = (data.get("display_name") or "").strip()
    password = data.get("password") or ""

    if not is_valid_email(email):
        return jsonify({"error": "valid email required"}), 400
    if not is_valid_display_name(display_name):
        return jsonify({"error": "display name required (1-50 chars)"}), 400
    if not is_valid_password(password, email=email):
        return (
            jsonify(
                {
                    "error": (
                        f"password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} "
                        "chars and cannot equal your email"
                    )
                }
            ),
            400,
        )
    if User.query.filter_by(email=email).first() is not None:
        return jsonify(UNABLE_TO_REGISTER[0]), UNABLE_TO_REGISTER[1]

    user = User(email=email, display_name=display_name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Explicitly do NOT create a session — user must log in.
    return jsonify(user.to_dict()), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify(INVALID_CREDENTIALS[0]), INVALID_CREDENTIALS[1]

    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify(user.to_dict()), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return "", 204


@auth_bp.get("/me")
@login_required
def me():
    user = db.session.get(User, session["user_id"])
    if user is None:
        # Session referenced a deleted user; clear it.
        session.clear()
        return jsonify({"error": "authentication required"}), 401
    return jsonify(user.to_dict()), 200
