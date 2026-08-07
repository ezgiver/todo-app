from functools import wraps

from flask import jsonify, session

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 254
MIN_DISPLAY_NAME_LENGTH = 1
MAX_DISPLAY_NAME_LENGTH = 50


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "authentication required"}), 401
        return view(*args, **kwargs)

    return wrapper


def current_user_id() -> int | None:
    return session.get("user_id")


def is_valid_email(email: str) -> bool:
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False
    if email.count("@") != 1:
        return False
    local, _, domain = email.partition("@")
    if not local or not domain or "." not in domain:
        return False
    return True


def is_valid_password(password: str, *, email: str = "") -> bool:
    if not (MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH):
        return False
    if email and password.lower() == email.lower():
        return False
    return True


def is_valid_display_name(name: str) -> bool:
    return MIN_DISPLAY_NAME_LENGTH <= len(name) <= MAX_DISPLAY_NAME_LENGTH
