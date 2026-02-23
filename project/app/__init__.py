# project/app/__init__.py

import os
import time
from flask import Flask
from .extensions import limiter
from .routes import main as main_bp
from dotenv import load_dotenv
from datetime import datetime
from .logging_config import configure_logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .metrics import (
    http_requests_total,
    http_errors_total,
    calibration_executions_total,
    drift_events_total,
    service_uptime_seconds
)

load_dotenv()

def create_app(config_override: dict = None):
    """
    Application factory.
    All Flask setup lives here. This allows clean modular structure,
    testing, and future expansion.
    """

    app = Flask(__name__)

    # Configure structured logging
    configure_logging(app)

    # -------------------------------
    # Prometheus Request Tracking
    # -------------------------------
    @app.before_request
    def before_request():
        http_requests_total.inc()


    @app.after_request
    def after_request(response):
        if response.status_code >= 400:
            http_errors_total.inc()
        return response
    # -------------------------------
    # Default configuration
    # -------------------------------
    app.config.setdefault("LOG_MAX_BYTES", 512 * 1024)
    app.config.setdefault("LOG_BACKUPS", 5)
    app.config.setdefault("HONEY_POT_FIELD", "hp_1aa74582")
    app.config.setdefault("LIMITER_STORAGE_URI", "memory://")
    app.config.setdefault("DEFAULT_RATE_LIMITS", ["120 per minute"])
    app.config["MODEL_VERSION"] = os.getenv("MODEL_VERSION", "0.0.0")
    app.config["ENVIRONMENT"] = os.getenv("ENVIRONMENT", "development")

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

    # -------------------------------
    # Health Endpoints
    # -------------------------------
    start_time = time.time()

    @app.route("/health/live", methods=["GET"])
    def health_live():
        service_uptime_seconds.set(time.time() - start_time)

        return {
            "status": "alive",
            "uptime_seconds": round(time.time() - start_time, 2)
        }, 200


    @app.route("/health/ready", methods=["GET"])
    def health_ready():
        service_uptime_seconds.set(time.time() - start_time)

        checks = {
            "model_version_loaded": bool(app.config.get("MODEL_VERSION")),
            "environment_loaded": bool(app.config.get("ENVIRONMENT")),
        }

        all_ready = all(checks.values())

        status_code = 200 if all_ready else 503

        return {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "model_version": app.config.get("MODEL_VERSION"),
            "environment": app.config.get("ENVIRONMENT"),
            "uptime_seconds": round(time.time() - start_time, 2)
        }, status_code


    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    return app

 
