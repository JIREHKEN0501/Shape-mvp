# project/app/ml/integration/task_metadata_update.py

"""
Read-only integration of ML task difficulty outputs into task metadata.

This module:
- does NOT affect task execution
- does NOT alter declared difficulty
- does NOT personalize anything
- exists for inspection and human review only
"""

from typing import Dict, List
from copy import deepcopy


def attach_difficulty_insights(
    task_registry: Dict[str, Dict],
    difficulty_results: List[Dict],
) -> Dict[str, Dict]:
    """
    Attach ML-derived difficulty insights to task metadata.

    Args:
        task_registry: mapping task_id -> task metadata
        difficulty_results: outputs from task_difficulty_model_v0

    Returns:
        New task registry with ML insights attached (non-destructive)
    """

    updated_registry = deepcopy(task_registry)

    for result in difficulty_results:
        task_id = result["task_id"]

        if task_id not in updated_registry:
            continue

        updated_registry[task_id]["ml_insights"] = {
            "empirical_difficulty": result["empirical_difficulty"],
            "difficulty_delta": result["difficulty_delta"],
            "confidence": result["confidence"],
            "calibration_flag": result["calibration_flag"],
            "notes": result.get("notes", []),
            "model_version": "task_difficulty_v0",
        }

    return updated_registry
