import json
import time
from pathlib import Path
from typing import Dict, Any


def _project_root() -> Path:
    """
    Locate repository root.
    """

    return Path(__file__).resolve().parents[4]


def _trace_log_path() -> Path:
    """
    Path to routing trace log.
    """

    return (
        _project_root()
        / "logs"
        / "routing_trace_log.jsonl"
    )


def persist_routing_trace(
    participant_id: str,
    trace: Dict[str, Any],
    health: Dict[str, Any] | None = None
) -> None:
    """
    Persist routing transparency trace.

    IMPORTANT:
    Stored traces describe session-level routing behavior only.
    """

    payload = {
        "event_type": "routing_trace",

        "participant_id": participant_id,

        "timestamp": time.time(),

        "trace": trace
    }

    # =====================================
    # Optional orchestration health telemetry
    # =====================================

    if health is not None:

        payload["health"] = health

    log_path = _trace_log_path()

    # Ensure logs directory exists
    log_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with log_path.open(
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(payload)
        )

        f.write("\n")
