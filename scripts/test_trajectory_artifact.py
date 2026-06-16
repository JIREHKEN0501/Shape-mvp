import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.app.utils.trajectory_artifact import (
    build_trajectory_artifact,
)

participants = [
    {
        "participant_id": "hp_7f0db588",
        "attempts": 42,
        "accuracy": 100.0,
        "avg_hesitation": 1.55,
        "difficulty_1": 14,
        "difficulty_2": 16,
        "difficulty_3": 12,
    },
    {
        "participant_id": "hp_0b8b155b",
        "attempts": 42,
        "accuracy": 90.48,
        "avg_hesitation": 2.79,
        "difficulty_1": 14,
        "difficulty_2": 16,
        "difficulty_3": 12,
    },
    {
        "participant_id": "hp_225ffd49",
        "attempts": 42,
        "accuracy": 57.14,
        "avg_hesitation": 2.38,
        "difficulty_1": 14,
        "difficulty_2": 16,
        "difficulty_3": 12,
    },
    {
        "participant_id": "hp_d09b5ec8",
        "attempts": 42,
        "accuracy": 33.33,
        "avg_hesitation": 1.60,
        "difficulty_1": 14,
        "difficulty_2": 16,
        "difficulty_3": 12,
    },
]

for p in participants:
    artifact = build_trajectory_artifact(p)

    print("\n" + "=" * 60)
    print(artifact)
