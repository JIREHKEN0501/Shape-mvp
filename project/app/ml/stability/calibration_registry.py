# project/app/ml/stability/calibration_registry.py

"""
Calibration Registry

Purpose:
- Persist task-level calibration outputs over time
- Enable longitudinal stability and drift analysis
- Maintain append-only audit trail

Design Principles:
- Population-level only
- No session linking
- No participant identity
- Append-only JSONL storage
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

# ----------------------------------------
# Calibration Engine Version Metadata
# ----------------------------------------

CALIBRATION_ENGINE_VERSION = {
    "model_version": "difficulty_model_v0.3",
    "weights_version": "weights_v1",
    "ci_method": "bootstrap_v1",
    "stability_logic_version": "stability_v1",
    "drift_logic_version": "zscore_v1",
}

REGISTRY_PATH = "logs/calibration_registry.jsonl"


def _ensure_registry_exists():
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    if not os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "w"):
            pass


def record_calibration(calibration_output: Dict) -> None:
    """
    Append a calibration snapshot to registry.
    """
    _ensure_registry_exists()

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": calibration_output["task_id"],
        "empirical_difficulty": calibration_output["empirical_difficulty"],
        "declared_difficulty": calibration_output["declared_difficulty"],
        "confidence_interval_95": calibration_output.get("confidence_interval_95"),
        "confidence_level": calibration_output.get("confidence_level"),
        "calibration_flag": calibration_output.get("calibration_flag"),
        "engine_metadata": CALIBRATION_ENGINE_VERSION,
    }

    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


def get_task_history(task_id: str) -> List[Dict]:
    """
    Retrieve historical calibration records for a task.
    """
    if not os.path.exists(REGISTRY_PATH):
        return []

    history = []

    with open(REGISTRY_PATH, "r") as f:
        for line in f:
            record = json.loads(line)
            if record["task_id"] == task_id:
                history.append(record)

    return history


def get_recent_difficulties(task_id: str, window: int = 10) -> List[float]:
    """
    Return most recent empirical difficulties for drift detection.
    """
    history = get_task_history(task_id)
    difficulties = [r["empirical_difficulty"] for r in history]

    if window:
        return difficulties[-window:]

    return difficulties

