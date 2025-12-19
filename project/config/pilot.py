# project/config/pilot.py

class PilotConfig:
    ENV = "pilot"
    DEBUG = False

    # Strict rate limits for pilot reliability
    RATE_LIMIT_GLOBAL = "200 per hour"

    # Honeypot key (rotate before external pilots)
    HONEY_POT_FIELD = "hp_pilot_xyz"

    # Logging locations
    DATA_LOG = "logs/internal_pilot/data_log.jsonl"
    AUDIT_LOG = "logs/audit_log.jsonl"

    # Same secret but rotate BEFORE any school pilot
    SECRET_KEY = "replace_me_pilot_key"


