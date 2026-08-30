# project/app/__init__.py

import os

from flask import Flask

from .extensions import limiter
from .routes import main as main_bp
from .routes.security import (
    register_rate_limit_handler,
    register_honeypot_hooks,
)

def create_app(config_override: dict = None):
    """
    Canonical Flask application factory.

    All Flask setup lives here. This is the application construction
    path used by tests and deployment.
    """

    app = Flask(__name__)

    # -------------------------------
    # Default configuration
    # -------------------------------

    app.config.setdefault("LOG_MAX_BYTES", 512 * 1024)
    app.config.setdefault("LOG_BACKUPS", 5)
    app.config.setdefault("HONEY_POT_FIELD", "hp_1aa74582")
    app.config.setdefault(
        "RATELIMIT_STORAGE_URI",
        os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    )
    app.config.setdefault("DEFAULT_RATE_LIMITS", ["120 per minute"])

    # Flask session secret:
    # production/pilot must provide this through the environment.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "")

    if config_override:
        app.config.update(config_override)

    # Never allow a non-testing deployment to run without a session secret.
    if not app.config["SECRET_KEY"] and not app.config.get("TESTING"):
        raise RuntimeError(
            "SECRET_KEY must be configured through the environment."
        )

    # -------------------------------
    # Session cookie security
    # -------------------------------

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )

    # -------------------------------
    # Initialize extensions
    # -------------------------------

    limiter.init_app(app)
    register_rate_limit_handler(app)
    register_honeypot_hooks(app)

    # -------------------------------
    # Security headers
    # -------------------------------

    @app.after_request
    def security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin"
        response.headers["Cache-Control"] = "no-store"
        if os.environ.get("ENABLE_HSTS", "false").lower() == "true":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    # -------------------------------
    # Register blueprints
    # -------------------------------

    app.register_blueprint(main_bp)

    from project.app.routes.admin import admin_bp
    from project.app.routes.participant import participant_bp
    from project.app.routes.security import security_bp
    from project.app.routes.system import system_bp

    app.register_blueprint(security_bp)
    app.register_blueprint(participant_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(system_bp)

    return app
