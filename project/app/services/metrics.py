# project/app/services/metrics.py

"""
Metrics helpers for sessions.
For now, only basic behavioral metrics are implemented.
"""


def compute_behavioral_metrics(session: dict):
    """
    Very simple behavioral metrics placeholder.
    For now:
      - event_count: number of events
    """
    events = session.get("events") or []
    if not isinstance(events, list):
        events = []

    return {
        "event_count": len(events),
    }

