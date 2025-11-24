# project/app/routes.py
from flask import Blueprint, request, jsonify, render_template, make_response, redirect
from project.app.extensions import limiter

main = Blueprint("main", __name__)

# If you already have helper functions (audit_record, get_admin_token), import them.
# If they are in the old top-level app.py, create a small shim file and import from there.
try:
    # prefer new helpers module
    from .helpers import audit_record, get_admin_token
except Exception:
    # fallback: apps with older top-level app.py may expose these
    from app import audit_record, get_admin_token  # noqa: F401

@main.route("/", methods=["GET"])
def index():
    return "Shape MVP - running"

# Example: decoy_submit (JSON/form)
@main.route("/decoy_submit", methods=["POST"])
def decoy_submit():
    body = request.get_json(silent=True) or {}
    form = request.form or {}
    # build shallow fields dictionary (redact later)
    fields = {}
    fields.update({k: ("<redacted>" if "password" in k.lower() else v) for k, v in (body.items() if isinstance(body, dict) else [])})
    fields.update({k: ("<redacted>" if "password" in k.lower() else request.form.get(k)) for k in request.form.keys()})
    try:
        audit_record(action="decoy_hit", actor="unknown", subject=request.path, status="seen", extra={"ip": request.remote_addr, "fields": fields})
    except Exception:
        pass
    return render_template("decoy_thanks.html"), 200

# Add more endpoints: /snare, /fake-login, /admin/* etc — move your existing functions into this blueprint.

