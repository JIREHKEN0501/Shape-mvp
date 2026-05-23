import json

from pathlib import Path
from typing import List, Dict, Any


TRACE_LOG = Path(
    "logs/routing_trace_log.jsonl"
)


def load_recent_orchestration_history(
    participant_id: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Load recent orchestration traces for a participant.

    IMPORTANT:
    History describes orchestration behavior,
    not permanent participant characteristics.
    """

    if not TRACE_LOG.exists():

        return []

    matching_entries = []

    with TRACE_LOG.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:

                entry = json.loads(line)

            except json.JSONDecodeError:
                continue

            if (
                entry.get("participant_id")
                ==
                participant_id
            ):

                trace = entry.get(
                    "trace",
                    {}
                )

                health = entry.get(
                    "health",
                    {}
                )

                matching_entries.append({

                    "trace": trace,

                    "health": health
                })

    return matching_entries[-limit:]
