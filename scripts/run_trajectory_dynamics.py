import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.app.utils.trajectory_dynamics import (
    build_trajectory_dynamics,
)

TARGET_PARTICIPANT = "hp_0b8b155b"

attempts = []

with open("logs/data_log.jsonl", "r") as f:

    for line in f:

        try:
            event = json.loads(line)

        except Exception:
            continue

        if event.get("event_type") != "task_attempt":
            continue

        if (
            event.get("participant_id")
            != TARGET_PARTICIPANT
        ):
            continue

        metrics = event.get(
            "metrics",
            {},
        )

        attempts.append(
            {
                "is_correct": metrics.get(
                    "is_correct",
                    False,
                ),
                "hesitation": metrics.get(
                    "hesitation",
                    0,
                ),
                "difficulty": metrics.get(
                    "difficulty",
                    0,
                ),
            }
        )

result = build_trajectory_dynamics(
    attempts
)

print("\n=== TRAJECTORY DYNAMICS ===\n")

print(
    json.dumps(
        result,
        indent=2,
    )
)
