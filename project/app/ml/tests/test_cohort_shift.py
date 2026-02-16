from project.app.ml.stability.cohort_shift import detect_cohort_shift


def test_no_shift():
    baseline = {
        "empirical_difficulty": 0.6,
        "aggregated_metrics": {
            "accuracy_mean": 0.55,
            "avg_time_mean": 5.0,
        },
    }

    current = {
        "empirical_difficulty": 0.62,
        "aggregated_metrics": {
            "accuracy_mean": 0.54,
            "avg_time_mean": 5.1,
        },
    }

    result = detect_cohort_shift(baseline, current)

    assert result["status"] == "stable_population"


def test_detect_shift():
    baseline = {
        "empirical_difficulty": 0.4,
        "aggregated_metrics": {
            "accuracy_mean": 0.80,
            "avg_time_mean": 3.0,
        },
    }

    current = {
        "empirical_difficulty": 0.6,
        "aggregated_metrics": {
            "accuracy_mean": 0.60,
            "avg_time_mean": 5.0,
        },
    }

    result = detect_cohort_shift(baseline, current)

    assert result["status"] == "shift_detected"
    assert len(result["flags"]) > 0

