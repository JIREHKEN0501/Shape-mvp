import json
import datetime
import os
from jsonschema import validate, ValidationError

# SCHEMA_PATH points up one level to the schemas folder
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "behavioral_schema.json")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "test_data", "session_data.json")

# load schema once
with open(os.path.abspath(SCHEMA_PATH), "r") as f:
    SCHEMA = json.load(f)

print("DEBUG: Loaded schema path:", os.path.abspath(SCHEMA_PATH))
print("DEBUG: Schema 'required' keys:", SCHEMA.get("required"))

def _ensure_logfile():
    d = os.path.dirname(LOG_FILE)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

def log_event(event: dict):
    # ensure timestamp present (ISO + Z)
    if "timestamp" not in event or (event.get("timestamp") is None):
        event["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    try:
        validate(instance=event, schema=SCHEMA)
    except ValidationError as e:
        print("Validation error:", e.message)
        raise
    _ensure_logfile()
    # append safely
    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(event)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    print(f"Event logged: task_id={event.get('task_id')} participant={event.get('participant_id')}")
