# project/app/helpers.py

import json
import os
import time
import secrets
from flask import current_app


# -------------------------------
# Log file paths (always relative to project root)
# -------------------------------
AUDIT_LOG = "logs/audit_log.jsonl"
CONSENT_LOG = "logs/consent_log.jsonl"
DATA_LOG = "logs/data_log.jsonl"


# -------------------------------
# Audit logging
# -------------------------------
def audit_record(action, actor="unknown", subject=None, status="ok", extra=None):
    """
    Append a structured JSON audit log entry.
    This is a safe, non-breaking logger (never raises exceptions).
    """
    entry = {
        "ts": time.time(),
        "action": action,
        "actor": actor,
        "subject": subject,
        "status": status,
        "extra": extra or {},
    }

    try:
        os.makedirs("logs", exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        # Never break app flow due to logging
        pass


# -------------------------------
# Admin token loading
# -------------------------------
def get_admin_token():
    """
    Get the admin token from environment.
    Supports both:
    - ADMIN_TOKEN (legacy)
    - ADMIN_TOKEN_ACTIVE (new rotating scheme)
    """
    # Newer pattern: token rotation store
    token = os.environ.get("ADMIN_TOKEN_ACTIVE")
    if token:
        return token.strip()

    # Legacy pattern
    legacy = os.environ.get("ADMIN_TOKEN")
    if legacy:
        return legacy.strip()

    return None

def generate_participant_id():
    """
    Generate a new opaque participant identifier.
    Example: hp_1aa74582
    """
    return f"hp_{secrets.token_hex(4)}"

