# project/app/ml/tests/test_task_difficulty_model_v0.py

from project.app.ml.models.task_difficulty_model_v0 import compute_task_difficulty


def test_harder_than_declared_low_confidence():
    task_input = {
        "task_id": "pattern_completion_v1",
        "task_metadata": {
            "declared_difficulty": 0.4,
            "domain": "education",
            "structure_version": "1.0",
        },
        "aggregated_metrics": {
            "num_sessions": 42,
            "accuracy_mean": 0.52,
            "accuracy_std": 0.18,
            "avg_time_mean": 6.4,
            "avg_time_std": 1.9,
            "time_variance_mean": 2.3,
            "error_rate": 0.48,
        },
    }

    result = compute_task_difficulty(task_input)

    assert result["task_id"] == "pattern_completion_v1"
    assert result["empirical_difficulty"] > result["declared_difficulty"]
    assert result["calibration_flag"] == "low_confidence"
    assert result["notes"] != []


def test_aligned_task_high_confidence():
    task_input = {
        "task_id": "simple_arithmetic_v1",
        "task_metadata": {
            "declared_difficulty": 0.3,
            "domain": "education",
            "structure_version": "1.0",
        },
        "aggregated_metrics": {
            "num_sessions": 85,
            "accuracy_mean": 0.78,
            "accuracy_std": 0.05,
            "avg_time_mean": 2.1,
            "avg_time_std": 0.4,
            "time_variance_mean": 0.3,
            "error_rate": 0.22,
        },
    }

    result = compute_task_difficulty(task_input)

    assert abs(result["empirical_difficulty"] - 0.3) < 0.1
    assert result["calibration_flag"] == "aligned"
    assert result["confidence"] > 0.5
    assert result["notes"] == []


def test_output_bounds():
    task_input = {
        "task_id": "edge_case",
        "task_metadata": {
            "declared_difficulty": 0.0,
            "domain": "education",
            "structure_version": "1.0",
        },
        "aggregated_metrics": {
            "num_sessions": 1,
            "accuracy_mean": 1.0,
            "accuracy_std": 0.0,
            "avg_time_mean": 0.0,
            "avg_time_std": 0.0,
            "time_variance_mean": 0.0,
            "error_rate": 0.0,
        },
    }

    result = compute_task_difficulty(task_input)

    assert 0.0 <= result["empirical_difficulty"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
