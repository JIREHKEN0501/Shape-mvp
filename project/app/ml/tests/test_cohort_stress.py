import numpy as np
from project.app.ml.generators.session_simulator import simulate_sessions
from project.app.ml.aggregation.task_difficulty_aggregator import aggregate_sessions
from project.app.ml.models.task_difficulty_model_v0 import compute_task_difficulty


def test_large_cohort_stability():
    # Simulate 1000 sessions with moderate difficulty
    sessions = simulate_sessions(
        n_sessions=1000,
        true_difficulty=0.6,
        variance=0.1,
        time_mean=5.0,
        time_std=1.2
    )

    aggregated = aggregate_sessions(sessions)

    task_input = {
        "task_id": "stress_test_task",
        "task_metadata": {
            "declared_difficulty": 0.6,
            "domain": "education",
            "structure_version": "1.0",
        },
        "aggregated_metrics": aggregated,
    }

    result = compute_task_difficulty(task_input)

    # Stability expectations
    assert 0.5 <= result["empirical_difficulty"] <= 0.8
    assert result["calibration_flag"] in ["stable", "low_confidence", "high_confidence"]
    assert result["task_id"] == "stress_test_task"

