# project/app/services/sessions.py

"""
Session storage helpers.
Responsible for persisting session results to the data log.
"""

import os
import json
import time

from project.app.helpers import DATA_LOG


def save_session_result(session: dict):
    """
    Append the session to DATA_LOG as a JSON line.
    Adds a timestamp if missing. Returns the saved object.
    """
    if not isinstance(session, dict):
        session = {"raw": session}

    if "ts" not in session:
        session["ts"] = time.time()

    os.makedirs("logs", exist_ok=True)
    with open(DATA_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(session) + "\n")

    return session

