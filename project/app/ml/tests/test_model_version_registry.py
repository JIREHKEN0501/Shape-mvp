from project.app.ml.stability.calibration_registry import record_calibration
import json
import os

def test_registry_records_model_version(tmp_path):
    test_output = {
        "task_id": "t1",
        "model_version": "1.0.0",
        "empirical_difficulty": 0.5,
    }

    record_calibration(test_output)

    with open("logs/calibration_registry.jsonl") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

    assert last_entry["model_version"] == "1.0.0"
