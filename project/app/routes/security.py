# project/app/routes/security.py

from flask import request, jsonify, make_response, g
from functools import wraps
import os, secrets, hmac, hashlib

from flask_limiter.errors import RateLimitExceeded


# -------------------------
# SECURITY BLUEPRINT
# -------------------------
from flask import Blueprint

security_bp = Blueprint("security_bp", __name__)

@security_bp.route("/security/ping", methods=["GET"])
def security_ping():
    return jsonify({"ok": True, "message": "security blueprint loaded"}), 200

#
# ============================================================
#  ADMIN TOKEN HELPERS
# ============================================================
#

def get_admin_token() -> str:
    """Read rotating admin token from environment."""
    return os.environ.get("ADMIN_TOKEN", "").strip()


def extract_admin_token_from_request() -> str:
    """Extract token from:
       - Authorization: Bearer <token>
       - Authorization: <token>
       - X-ADMIN-TOKEN: <token>
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()

    return (
        request.headers.get("X-ADMIN-TOKEN", "").strip()
        or auth.strip()
    )


#
# ============================================================
#  ADMIN DECORATOR
# ============================================================
#

def admin_required(f):
    """Protect sensitive admin endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        real = get_admin_token()
        if not real:
            return jsonify({"error": "Admin token not configured"}), 500

        provided = extract_admin_token_from_request()
        if provided != real:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper


#
# ============================================================
#  RATE LIMIT JSON HANDLER
# ============================================================
#

def register_rate_limit_handler(app):
    """Attach global JSON error for rate limit violations."""

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        retry = getattr(e, "reset_in", 1)
        resp = jsonify({"error": "rate_limited", "retry_after": retry})
        resp.status_code = 429
        resp.headers["Retry-After"] = str(retry)
        return resp


#
# ============================================================
#  HOST GUARD (allow single host only)
# ============================================================
#

ALLOWED_ORIGIN_HOST = os.environ.get("ALLOWED_ORIGIN_HOST", "127.0.0.1")

def register_host_guard(app):
    @app.before_request
    def host_siteguard():
        # TEMP DISABLED FOR LOCAL DEV
            return None


#
# ============================================================
#  HONEYPOT FIELD (signed)
# ============================================================
#

HMAC_KEY = os.environ.get("HMAC_KEY")
if not HMAC_KEY:
    # local dev fallback only
    HMAC_KEY = secrets.token_hex(32)


def generate_honeypot_field():
    return "hp_" + secrets.token_hex(4)


def sign_val(val: str) -> str:
    key = HMAC_KEY.encode("utf-8")
    return hmac.new(key, val.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_val(val: str, sig: str) -> bool:
    key = HMAC_KEY.encode("utf-8")
    expected = hmac.new(key, val.encode("utf-8"),
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


#
# Ensure honeypot cookie exists
#
def register_honeypot_hooks(app):
    @app.before_request
    def rotate_honeypot_cookie():
        try:
            raw = request.cookies.get("hp_field", "")
            valid = None

            if raw and "|" in raw:
                name, sig = raw.split("|", 1)
                if name.startswith("hp_") and verify_val(name, sig):
                    valid = name

            if not valid:
                new_name = generate_honeypot_field()
                sig = sign_val(new_name)
                g.hp_cookie_to_set = f"{new_name}|{sig}"

        except Exception:
            pass

    @app.after_request
    def apply_honeypot_cookie(resp):
        try:
            if hasattr(g, "hp_cookie_to_set"):
                resp.set_cookie(
                    "hp_field",
                    g.hp_cookie_to_set,
                    max_age=60 * 60 * 24,
                    httponly=False,
                    samesite="Lax",
                    path="/"
                )
        except Exception:
            pass

        return resp


#
# ============================================================
#  BOT TRIPWIRE
# ============================================================
#

def bot_tripwire():
    """Block if honeypot field is filled."""
    hp_name = None
    honeypot_val = None

    # Signed cookie preferred
    try:
        raw = request.cookies.get("hp_field", "")
        if raw and "|" in raw:
            name, sig = raw.split("|", 1)
            if name.startswith("hp_") and verify_val(name, sig):
                hp_name = name
    except Exception:
        hp_name = None

    if not hp_name:
        hp_name = os.environ.get("HONEYPOT_FIELD", "hp_website")

    # Extract field from JSON or form
    if request.is_json:
        body = request.get_json(silent=True) or {}
        honeypot_val = (body.get(hp_name) or "").strip()
    else:
        honeypot_val = (request.form.get(hp_name) or "").strip()

    # Check querystring too
    if not honeypot_val:
        honeypot_val = (request.args.get(hp_name) or "").strip()

    if honeypot_val:
        return jsonify({"error": "bot_detected"}), 400

    return None

