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
from typing import Dict, List
from uuid import uuid4

# ----------------------------------------
# Calibration Engine Version Metadata
# ----------------------------------------

CALIBRATION_ENGINE_VERSION = {
    "model_version": "1.0.0",
    "algorithm": "weighted_signal_difficulty",
    "bayesian_layer": "conjugate_analytical",
    "confidence_interval_method": "bootstrap_or_normal_fallback",
    "drift_detection": "z_score_population_level",
    "stability_gating": "confidence_interval_overlap",
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
        "calibration_snapshot_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": calibration_output["task_id"],
        "empirical_difficulty": calibration_output["empirical_difficulty"],
        "declared_difficulty": calibration_output["declared_difficulty"],
        "difficulty_delta": calibration_output.get("difficulty_delta"),
        "confidence": calibration_output.get("confidence"),
        "confidence_interval_95": calibration_output.get(
            "confidence_interval_95"
        ),
        "sample_size": calibration_output.get("sample_size"),
        "confidence_level": calibration_output.get("confidence_level"),
        "calibration_flag": calibration_output.get("calibration_flag"),
        "drift": calibration_output.get("drift"),
        "engine_metadata": dict(CALIBRATION_ENGINE_VERSION),
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

