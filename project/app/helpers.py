# project/app/helpers.py
# Temporary shim: import helpers from the top-level app module (if present).
# Later you should move implementations here and remove circular imports.

try:
    from app import audit_record, get_admin_token, AUDIT_LOG, CONSENT_LOG, DATA_LOG  # pragma: no cover
except Exception:
    # If not found, provide safe no-op defaults
    def audit_record(*args, **kwargs):  # pragma: no cover
        return None

    def get_admin_token():  # pragma: no cover
        return None

    AUDIT_LOG = "logs/audit_log.jsonl"
    CONSENT_LOG = "logs/consent_log.jsonl"
    DATA_LOG = "logs/data_log.jsonl"

