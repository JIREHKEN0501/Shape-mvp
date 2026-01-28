# project/app/__init__.py

from flask import Flask
from .extensions import limiter
from .routes import main as main_bp

def create_app(config_override: dict = None):
    """
    Application factory.
    All Flask setup lives here. This allows clean modular structure,
    testing, and future expansion.
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
    # Initialize extensions
    # -------------------------------
    limiter.init_app(app)

    # -------------------------------
    # Register blueprints
    # -------------------------------
    app.register_blueprint(main_bp)

    # Admin blueprint
    from project.app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Participant blueprint (NEW)
    from project.app.routes.participant import participant_bp
    app.register_blueprint(participant_bp)
   
    # Submit result blueprint 
    from project.app.routes.submit_result import submit_result_bp
    app.register_blueprint(submit_result_bp)

    return app
