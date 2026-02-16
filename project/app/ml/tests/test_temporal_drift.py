from project.app.ml.stability.temporal_drift import detect_temporal_drift


def test_no_drift():
    history = [
        {
            "empirical_difficulty": 0.60,
            "aggregated_metrics": {"accuracy_mean": 0.55, "avg_time_mean": 5.0},
        },
        {
            "empirical_difficulty": 0.61,
            "aggregated_metrics": {"accuracy_mean": 0.56, "avg_time_mean": 5.1},
        },
        {
            "empirical_difficulty": 0.59,
            "aggregated_metrics": {"accuracy_mean": 0.54, "avg_time_mean": 4.9},
        },
    ]

    result = detect_temporal_drift(history)

    assert result["status"] == "stable"


def test_detect_difficulty_drift():
    history = [
        {
            "empirical_difficulty": 0.40,
            "aggregated_metrics": {"accuracy_mean": 0.80, "avg_time_mean": 3.0},
        },
        {
            "empirical_difficulty": 0.50,
            "aggregated_metrics": {"accuracy_mean": 0.70, "avg_time_mean": 4.0},
        },
        {
            "empirical_difficulty": 0.65,
            "aggregated_metrics": {"accuracy_mean": 0.60, "avg_time_mean": 5.0},
        },
    ]

    result = detect_temporal_drift(history)

    assert result["status"] == "drift_detected"
    assert "difficulty_drift" in result["flags"]

