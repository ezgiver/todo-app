import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from .extensions import db
from .routes.auth import auth_bp
from .routes.health import health_bp
from .routes.todos import todos_bp


def create_app(config_object: str = "config.DevelopmentConfig") -> Flask:
    static_root = os.environ.get("STATIC_ROOT")
    has_spa = bool(static_root) and os.path.isfile(
        os.path.join(static_root, "index.html")
    )

    kwargs = {"instance_relative_config": True}
    if has_spa:
        kwargs["static_folder"] = static_root
        kwargs["static_url_path"] = "/static"

    app = Flask(__name__, **kwargs)
    app.config.from_object(config_object)

    _validate_secret_key(app)

    _ensure_instance_folder(app)
    db.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
        supports_credentials=True,
    )

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(todos_bp, url_prefix="/api/todos")

    if has_spa:
        _register_spa(app)

    _register_error_handlers(app)

    with app.app_context():
        # Auto-create tables in dev; swap for Flask-Migrate before prod.
        db.create_all()

    return app


def _validate_secret_key(app: Flask) -> None:
    key = app.config.get("SECRET_KEY")
    if not key:
        raise RuntimeError(
            "SECRET_KEY is not set. Refusing to start."
            " Set the SECRET_KEY environment variable."
        )
    if not app.debug and not app.testing and key == "dev-only-not-for-prod":
        raise RuntimeError(
            "Refusing to start with the dev placeholder SECRET_KEY in production."
        )


def _ensure_instance_folder(app: Flask) -> None:
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass


def _register_spa(app: Flask) -> None:
    """Serve the built React app + fall back to index.html for client-side routing."""

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path: str):
        candidate = os.path.join(app.static_folder, path)
        if path and os.path.isfile(candidate):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(_e):
        return jsonify({"error": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "internal server error"}), 500
