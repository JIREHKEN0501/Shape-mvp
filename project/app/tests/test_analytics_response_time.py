from project.app.services.analytics import (
    _augment_attempts_with_metrics_and_time,
)


def test_augment_attempts_prefers_latency_ms_over_session_elapsed_time():
    attempts = [
        {
            "participant_id": "participant-1",
            "task_id": "attention_001",
            "ts": 110.0,
            "metrics": {
                "is_correct": True,
                "category": "attention",
                "difficulty": 1,
                "latency_ms": 2500,
                "hesitation": 0,
            },
        }
    ]

    sessions = [
        {
            "participant_id": "participant-1",
            "ts": 100.0,
        }
    ]

    enriched = _augment_attempts_with_metrics_and_time(
        attempts,
        sessions,
    )

    assert len(enriched) == 1
    assert enriched[0]["response_time_s"] == 2.5


def test_augment_attempts_falls_back_to_session_elapsed_time_without_latency():
    attempts = [
        {
            "participant_id": "participant-1",
            "task_id": "attention_001",
            "ts": 110.0,
            "metrics": {
                "is_correct": True,
                "category": "attention",
                "difficulty": 1,
            },
        }
    ]

    sessions = [
        {
            "participant_id": "participant-1",
            "ts": 100.0,
        }
    ]

    enriched = _augment_attempts_with_metrics_and_time(
        attempts,
        sessions,
    )

    assert len(enriched) == 1
    assert enriched[0]["response_time_s"] == 10.0
