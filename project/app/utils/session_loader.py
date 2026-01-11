# project/app/utils/session_loader.py

import json
from pathlib import Path

DATA_LOG_PATH = Path("project/logs/data_log.jsonl")


def load_session_by_id(session_id: str) -> dict | None:
    """
    Load a single session by session_id from the data log.

    Returns:
        dict if found
        None if not found
    """
    if not DATA_LOG_PATH.exists():
        return None

    with DATA_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if record.get("session_id") == session_id:
                return record

    return None

