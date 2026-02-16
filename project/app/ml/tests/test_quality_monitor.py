from project.app.ml.quality.data_quality_monitor import evaluate_aggregation_quality


def test_valid_aggregation():
    metrics = {
        "num_sessions": 100,
        "accuracy_mean": 0.65,
        "accuracy_std": 0.12,
        "avg_time_mean": 5.2,
        "avg_time_std": 1.1,
        "time_variance_mean": 2.4,
        "error_rate": 0.35,
    }

    result = evaluate_aggregation_quality(metrics)

    assert result["is_valid"] is True
    assert result["quality_flags"] == []


def test_insufficient_sample_flag():
    metrics = {
        "num_sessions": 10,
        "accuracy_mean": 0.65,
        "accuracy_std": 0.12,
        "avg_time_mean": 5.2,
        "avg_time_std": 1.1,
        "time_variance_mean": 2.4,
        "error_rate": 0.35,
    }

    result = evaluate_aggregation_quality(metrics)

    assert result["is_valid"] is False
    assert "insufficient_sample_size" in result["quality_flags"]
