from flask import Flask, jsonify
from flask_cors import CORS

from .extensions import db
from .routes.todos import todos_bp


def create_app(config_object: str = "config.DevelopmentConfig") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    _ensure_instance_folder(app)
    db.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
        supports_credentials=False,
    )

    app.register_blueprint(todos_bp, url_prefix="/api/todos")

    _register_error_handlers(app)

    with app.app_context():
        # Auto-create tables in dev; swap for Flask-Migrate before prod.
        db.create_all()

    return app


def _ensure_instance_folder(app: Flask) -> None:
    try:
        import os
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass


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
