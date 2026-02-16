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
        "confidence_interval_95": (0.58, 0.66),
        "confidence_level": "high",
        "calibration_flag": "aligned",
    }

    record_calibration(calibration)
    history = get_task_history("t1")

    assert len(history) == 1
    assert history[0]["task_id"] == "t1"
    assert history[0]["empirical_difficulty"] == 0.62

