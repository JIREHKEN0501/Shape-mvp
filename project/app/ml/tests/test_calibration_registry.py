from project.app.ml.stability.calibration_registry import (
    record_calibration,
    get_task_history,
)

def test_registry_records_and_retrieves(tmp_path, monkeypatch):
    test_file = tmp_path / "registry.jsonl"

    monkeypatch.setattr(
        "project.app.ml.stability.calibration_registry.REGISTRY_PATH",
        str(test_file),
    )

    calibration = {
        "task_id": "t1",
        "empirical_difficulty": 0.62,
        "declared_difficulty": 0.60,
        "difficulty_delta": 0.02,
        "confidence": 0.82,
        "confidence_interval_95": (0.58, 0.66),
        "sample_size": 120,
        "confidence_level": "high",
        "calibration_flag": "aligned",
        "drift": None,
    }

    record_calibration(calibration)
    history = get_task_history("t1")

    assert len(history) == 1
    assert history[0]["task_id"] == "t1"
    assert history[0]["empirical_difficulty"] == 0.62

    assert history[0]["calibration_snapshot_id"]
    assert history[0]["difficulty_delta"] == 0.02
    assert history[0]["confidence"] == 0.82
    assert history[0]["sample_size"] == 120
    assert history[0]["drift"] is None

    assert history[0]["engine_metadata"]["model_version"] == "1.0.0"
    assert (
        history[0]["engine_metadata"]["algorithm"]
        == "weighted_signal_difficulty"
    )

def test_registry_assigns_unique_snapshot_ids(tmp_path, monkeypatch):
    test_file = tmp_path / "registry.jsonl"
    monkeypatch.setattr(
        "project.app.ml.stability.calibration_registry.REGISTRY_PATH",
        str(test_file),
    )

    calibration = {
        "task_id": "t1",
        "empirical_difficulty": 0.62,
        "declared_difficulty": 0.60,
        "difficulty_delta": 0.02,
        "confidence": 0.82,
        "confidence_interval_95": (0.58, 0.66),
        "sample_size": 120,
        "confidence_level": "high",
        "calibration_flag": "aligned",
        "drift": None,
    }

    record_calibration(calibration)
    record_calibration(calibration)

    history = get_task_history("t1")

    assert len(history) == 2
    assert history[0]["calibration_snapshot_id"]
    assert history[1]["calibration_snapshot_id"]
    assert (
        history[0]["calibration_snapshot_id"]
        != history[1]["calibration_snapshot_id"]
    )
