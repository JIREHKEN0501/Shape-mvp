from project.app.ml.monitoring.task_drift_monitor import detect_task_drift


def test_stable_series():
    series = [
        {"period": "m1", "empirical_difficulty": 0.6},
        {"period": "m2", "empirical_difficulty": 0.61},
        {"period": "m3", "empirical_difficulty": 0.59},
        {"period": "m4", "empirical_difficulty": 0.6},
    ]

    result = detect_task_drift(series)
    assert result["trend"] == "stable"
    assert result["drift_flag"] == "no_drift"


def test_gradual_increase():
    series = [
        {"period": "m1", "empirical_difficulty": 0.5},
        {"period": "m2", "empirical_difficulty": 0.55},
        {"period": "m3", "empirical_difficulty": 0.6},
        {"period": "m4", "empirical_difficulty": 0.65},
    ]

    result = detect_task_drift(series)
    assert result["trend"] in ["gradual_shift", "abrupt_shift"]
    assert result["drift_flag"] == "drift_up"


def test_gradual_decrease():
    series = [
        {"period": "m1", "empirical_difficulty": 0.7},
        {"period": "m2", "empirical_difficulty": 0.65},
        {"period": "m3", "empirical_difficulty": 0.6},
        {"period": "m4", "empirical_difficulty": 0.55},
    ]

    result = detect_task_drift(series)
    assert result["drift_flag"] == "drift_down"


def test_insufficient_points():
    series = [
        {"period": "m1", "empirical_difficulty": 0.6},
        {"period": "m2", "empirical_difficulty": 0.61},
    ]

    result = detect_task_drift(series)
    assert result["trend"] == "insufficient_data"

