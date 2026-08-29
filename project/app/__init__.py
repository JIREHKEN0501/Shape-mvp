# project/app/__init__.py

from flask import Flask

from .extensions import limiter
from .routes import main as main_bp


def create_app(config_override: dict = None):
    """
    Canonical Flask application factory.

    All Flask setup lives here. This is the application construction
    path used by tests and, after consolidation, deployment.
    """

    app = Flask(__name__)

    # -------------------------------
    # Default configuration
    # -------------------------------

    app.config.setdefault("LOG_MAX_BYTES", 512 * 1024)
    app.config.setdefault("LOG_BACKUPS", 5)
    app.config.setdefault("HONEY_POT_FIELD", "hp_1aa74582")
    app.config.setdefault("LIMITER_STORAGE_URI", "memory://")
    app.config.setdefault("DEFAULT_RATE_LIMITS", ["120 per minute"])

    if config_override:
        app.config.update(config_override)

    # -------------------------------
    # Security headers
    # -------------------------------

    @app.after_request
    def security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    # -------------------------------
    # Initialize extensions
    # -------------------------------

    limiter.init_app(app)

    # -------------------------------
    # Register security hooks
    # -------------------------------

    from project.app.routes.security import (
        register_rate_limit_handler,
        register_host_guard,
        register_honeypot_hooks,
    )

    register_rate_limit_handler(app)
    register_host_guard(app)
    register_honeypot_hooks(app)

    # -------------------------------
    # Register blueprints
    # -------------------------------

    app.register_blueprint(main_bp)

    from project.app.routes.security import security_bp
    app.register_blueprint(security_bp)

    from project.app.routes.system import system_bp
    app.register_blueprint(system_bp)

    from project.app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from project.app.routes.participant import participant_bp
    app.register_blueprint(participant_bp)

    from project.app.routes.submit_result import submit_result_bp
    app.register_blueprint(submit_result_bp)

    return app
