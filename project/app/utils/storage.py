# project/app/utils/storage.py

import json
import os
from datetime import datetime
from project.app.utils.helpers import now_iso

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

DATA_LOG = os.path.join(LOG_DIR, "data_log.jsonl")

# Make sure log dir exists
os.makedirs(LOG_DIR, exist_ok=True)

def append_jsonl(path: str, obj: dict):
    """Append a single JSON object to a .jsonl file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def save_session_result(session: dict) -> dict:
    """
    Store a behavioral or cognitive session object in data_log.jsonl.
    Adds a timestamp.
    Returns the saved object.
    """
    if not isinstance(session, dict):
        raise ValueError("session must be dict")

    out = dict(session)
    out["saved_ts"] = now_iso()

    append_jsonl(DATA_LOG, out)
    return out

