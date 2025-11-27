# project/app/__init__.py
from flask import Flask
from .extensions import limiter
from .routes import main as main_bp

def create_app(config_override: dict = None):
    """
    App factory. Call create_app() to get a Flask app instance.
    config_override: dict of config values to override (useful for tests).
    """
    app = Flask(__name__, instance_relative_config=False)

    # sensible default config - you can set via environment or override
    app.config.setdefault("LOG_MAX_BYTES", 512 * 1024)
    app.config.setdefault("LOG_BACKUPS", 5)
    app.config.setdefault("HONEY_POT_FIELD", "hp_1aa74582")
    app.config.setdefault("LIMITER_STORAGE_URI", "memory://")
    app.config.setdefault("DEFAULT_RATE_LIMITS", ["120 per minute"])

    # apply runtime overrides (tests or run script may pass values)
    if config_override:
        app.config.update(config_override)

    # init extensions
    limiter.init_app(app)

    # register blueprints
    app.register_blueprint(main_bp)

    # keep compatibility: set module-level attributes used by older imports
    # e.g. you can still import "from app import app" if you want by calling:
    # from project.app import create_app; app = create_app()
    return app

