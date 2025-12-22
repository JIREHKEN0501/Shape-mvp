# project/app/utils/helpers.py

import hashlib
import time
import json
import os

def now_iso():
    """Return UTC timestamp in ISO-8601 format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def ip_hash(ip: str) -> str:
    """Hash IP addresses using SHA256 (privacy-safe)."""
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

def _read_jsonl_file(path):
    """Yield each JSONL line as a dict, safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except FileNotFoundError:
        return []

def _read_json_file(path):
    """Read a standard JSON file safely. Return (exists, data)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return True, json.load(f)
    except FileNotFoundError:
        return False, None
    except Exception:
        return True, None  # exists but invalid JSON

def _anonymize_and_replace_in_file(path, participant_id, replacement="***"):
    """Replace participant_id in a .jsonl file (in-place)."""
    try:
        temp_path = path + ".tmp"
        with open(path, "r", encoding="utf-8") as fin, open(temp_path, "w", encoding="utf-8") as fout:
            for line in fin:
                fout.write(line.replace(participant_id, replacement))
        os.replace(temp_path, path)
        return True
    except Exception:
        return False

def _count_jsonl_lines(path):
    """Return number of lines in a JSONL file, or None if unreadable."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return None

