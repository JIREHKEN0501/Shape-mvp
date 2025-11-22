import time
from project.analyze_events import (
    compute_behavioral_metrics,
    compute_cognitive_metrics,
)

# ---------------------------
# Behavioral metrics tests
# ---------------------------

def test_behavioral_basic():
    now = int(time.time() * 1000)
    s = {
        "participant_id": "t1",
        "task_id": "p1",
        "start_ts": now,
        "end_ts": now + 3000,  # 3.0s
        "events": [
            {"type": "keypress", "ts": now + 100},
            {"type": "hint",     "ts": now + 2600},  # gap 2500ms (>1500) triggers hesitation
        ],
    }
    m = compute_behavioral_metrics(s)
    assert m["type"] == "behavioral"
    assert m["total_time_ms"] == 3000
    assert m["hints_used"] == 1
    assert m["retries"] == 0
    assert m["keypress_count"] == 1
    # hesitation should include the >1500ms gap
    assert m["hesitation_ms"] >= 1500
    assert 0 < m["performance_score"] <= 100

# ---------------------------
# Cognitive metrics tests
# ---------------------------

def test_cognitive_basic():
    s = {
        "modules": [
            {
                "module_name": "m1",
                "questions": [
                    {"correct": True,  "time_taken_seconds": 10, "hesitation_seconds": 2, "retries": 0},
                    {"correct": False, "time_taken_seconds": 20, "hesitation_seconds": 4, "retries": 1},
                ],
            }
        ]
    }
    m = compute_cognitive_metrics(s)
    assert m["type"] == "cognitive"
    assert m["questions"] == 2
    assert m["avg_accuracy"] == 50.0
    assert round(m["avg_time_seconds"], 2) == 15.0
    assert round(m["avg_hesitation_seconds"], 2) == 3.0
    assert round(m["avg_retries"], 2) == 0.5


def test_cognitive_empty_modules_is_safe():
    s = {"modules": []}
    m = compute_cognitive_metrics(s)
    assert m["type"] == "cognitive"
    assert m["modules"] == 0
    assert m["avg_accuracy"] == 0
