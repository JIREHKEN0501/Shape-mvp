# project/app/utils/logging.py

import json
import os
import time
import hashlib
from flask import request

# ----------------------------------------------------
# Base paths
# ----------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
LOG_DIR = os.path.join(ROOT_DIR, "logs")

CONSENT_LOG = os.path.join(LOG_DIR, "consent_log.jsonl")
EXPERIENCE_LOG = os.path.join(LOG_DIR, "experience_log.jsonl")
DATA_LOG = os.path.join(LOG_DIR, "data_log.jsonl")
AUDIT_LOG = os.path.join(LOG_DIR, "audit_log.jsonl")

os.makedirs(LOG_DIR, exist_ok=True)

# ----------------------------------------------------
# Time helper
# ----------------------------------------------------

def now_iso():
    """Return UTC timestamp ISO-8601."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# ----------------------------------------------------
# JSONL append helper
# ----------------------------------------------------

def append_jsonl_secure(path, obj):
    """Append JSON safely to a .jsonl file."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as e:
        print("LOGGING ERROR:", e)

# ----------------------------------------------------
# Audit logger
# ----------------------------------------------------

def audit_record(action: str,
                 actor: str = None,
                 subject: str = None,
                 status: str = None,
                 extra: dict | None = None,
                 notes: str | None = None):
    """
    Append a structured audit log entry.
    Matches legacy behavior so new routes do not break.
    """
    if notes:
        if isinstance(extra, dict) and extra:
            extra = {"notes": notes, **extra}
        else:
            extra = {"notes": notes}

    try:
        rec = {
            "ts": now_iso(),
            "ip": request.remote_addr if request else None,
            "action": action,
            "actor": actor,
            "subject": subject,
            "status": status,
            "extra": extra or {},
        }
    except RuntimeError:
        # In case "request" is unavailable
        rec = {
            "ts": now_iso(),
            "ip": None,
            "action": action,
            "actor": actor,
            "subject": subject,
            "status": status,
            "extra": extra or {},
        }

    append_jsonl_secure(AUDIT_LOG, rec)

