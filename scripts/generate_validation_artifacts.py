import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.app.utils.trajectory_artifact import (
    build_trajectory_artifact,
)

LOG_FILE = "logs/data_log.jsonl"

TARGET_PARTICIPANTS = [
    "hp_7f0db588",
    "hp_0b8b155b",
    "hp_225ffd49",
    "hp_d09b5ec8",
]

participants = {}

with open(LOG_FILE, "r") as f:
    for line in f:
        try:
            event = json.loads(line)
        except Exception:
            continue

        if event.get("event_type") != "task_attempt":
            continue

        pid = event.get("participant_id")

        if pid not in TARGET_PARTICIPANTS:
            continue

        if pid not in participants:
            participants[pid] = {
                "participant_id": pid,
                "attempts": 0,
                "correct": 0,
                "hesitation_sum": 0,
                "difficulty_1": 0,
                "difficulty_2": 0,
                "difficulty_3": 0,
            }

        metrics = event.get("metrics", {})

        participants[pid]["attempts"] += 1

        if metrics.get("is_correct"):
            participants[pid]["correct"] += 1

        participants[pid]["hesitation_sum"] += (
            metrics.get("hesitation", 0)
        )

        difficulty = metrics.get("difficulty")

        if difficulty == 1:
            participants[pid]["difficulty_1"] += 1

        elif difficulty == 2:
            participants[pid]["difficulty_2"] += 1

        elif difficulty == 3:
            participants[pid]["difficulty_3"] += 1


print("\n=== VALIDATION ARTIFACTS ===\n")

for pid, stats in participants.items():

    attempts = stats["attempts"]

    accuracy = round(
        (stats["correct"] / attempts) * 100,
        2,
    )

    avg_hesitation = round(
        stats["hesitation_sum"] / attempts,
        2,
    )

    artifact_input = {
        "participant_id": pid,
        "attempts": attempts,
        "accuracy": accuracy,
        "avg_hesitation": avg_hesitation,
        "difficulty_1": stats["difficulty_1"],
        "difficulty_2": stats["difficulty_2"],
        "difficulty_3": stats["difficulty_3"],
    }

    artifact = build_trajectory_artifact(
        artifact_input
    )

    print("=" * 60)
    print(json.dumps(artifact, indent=2))
