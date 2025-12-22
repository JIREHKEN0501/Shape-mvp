# project/app/app.py

import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --------------------------
# ENV + BASE DIRECTORIES
# --------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure required directories exist
os.makedirs(LOG_DIR, exist_ok=True)

# --------------------------
# FLASK APP INITIALIZATION
# --------------------------

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "app", "templates"),
        static_folder=os.path.join(BASE_DIR, "app", "static")
    )

    # --------------------------
    # RATE LIMITER
    # --------------------------
    app.limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=os.environ.get("LIMITER_STORAGE_URI", "memory://"),
        default_limits=["200 per day", "50 per hour"],
        headers_enabled=True,
    )

    # --------------------------
    # SECURITY HEADERS
    # --------------------------
    @app.after_request
    def security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    # --------------------------
    # REGISTER BLUEPRINTS
    # --------------------------

    from project.app.routes.security import security_bp
    from project.app.routes.participant import participant_bp
    from project.app.routes.admin import admin_bp
    from project.app.routes.system import system_bp

    app.register_blueprint(security_bp)
    app.register_blueprint(participant_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(system_bp)

    # --------------------------
    # ROOT INDEX -> REDIRECT
    # --------------------------
    @app.route("/")
    def root():
        return {
            "ok": True,
            "message": "Cognitive-Behavioral Analytics MVP — API online",
            "routes": {
                "consent": "/consent",
                "submit_result": "/submit_result",
                "system_status": "/status",
                "metadata": "/metadata",
                "admin_login": "/admin/login",
                "admin_dashboard": "/admin/dashboard",
            }
        }, 200

    return app


# --------------------------
# ENTRYPOINT FOR FLASK CLI
# --------------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

