import json

from project.app.services.analytics import (
    _extract_experience_task_attempts,
    generate_experience_summary,
)


def _write_experience_records(path):
    records = [
        {
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "session_id": "session-1",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "pattern_1",
                    "questions": [
                        {
                            "question_id": "pr_q1",
                            "user_answer": "I",
                            "correct": "I",
                            "time_taken_seconds": 6,
                        },
                        {
                            "question_id": "pr_q2",
                            "user_answer": "30",
                            "correct": "30",
                            "time_taken_seconds": 7,
                        },
                    ],
                }
            ],
        },
        {
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "session_id": "session-2",
            "task_id": "strategy_under_constraint_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "allocation_round_1",
                    "questions": [
                        {
                            "question_id": "suc_q1",
                            "user_answer": "Secure immediate stability",
                            "correct": None,
                            "time_taken_seconds": 19,
                        },
                        {
                            "question_id": "suc_q2",
                            "user_answer": "Balance speed with safeguards",
                            "correct": None,
                            "time_taken_seconds": 20,
                        },
                    ],
                }
            ],
        },
    ]

    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def test_experience_task_attempts_are_scoped_to_experience(
    monkeypatch,
    tmp_path,
):
    log_file = tmp_path / "data_log.jsonl"
    _write_experience_records(log_file)

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    from project.app.services.analytics import _load_all_records

    records = _load_all_records()

    attempts = _extract_experience_task_attempts(
        records,
        "experience-1",
    )

    assert len(attempts) == 4

    assert all(
        attempt.get("experience_id") == "experience-1"
        for attempt in attempts
    )

    assert {
        attempt.get("task_id")
        for attempt in attempts
    } == {
        "pattern_recognition_v1",
        "strategy_under_constraint_v1",
    }


def test_experience_summary_preserves_objective_and_decision_boundaries(
    monkeypatch,
    tmp_path,
):
    log_file = tmp_path / "data_log.jsonl"
    _write_experience_records(log_file)

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    summary = generate_experience_summary("experience-1")

    assert summary["has_data"] is True
    assert summary["experience_id"] == "experience-1"
    assert summary["total_questions"] == 4
    assert summary["objective_questions"] == 2
    assert summary["decision_observations"] == 2
    assert summary["correct_objective_questions"] == 2
    assert summary["objective_accuracy"] == 1.0

    pattern = summary["tasks"]["pattern_recognition_v1"]
    strategy = summary["tasks"]["strategy_under_constraint_v1"]

    assert pattern["objective_questions"] == 2
    assert pattern["decision_observations"] == 0
    assert pattern["correct"] == 2
    assert pattern["accuracy"] == 1.0

    assert strategy["objective_questions"] == 0
    assert strategy["decision_observations"] == 2
    assert strategy["accuracy"] is None


def test_experience_temporal_analysis_does_not_overinterpret_small_sample(
    monkeypatch,
    tmp_path,
):
    log_file = tmp_path / "data_log.jsonl"
    _write_experience_records(log_file)

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    summary = generate_experience_summary("experience-1")

    assert summary["has_data"] is True

    temporal = summary.get("temporal_behavior")

    if temporal is not None:
        assert temporal.get("status") in {
            "insufficient_data",
            "analysis_unavailable",
        }

def test_generate_experience_summary_isolates_experience_records(
    monkeypatch,
    tmp_path,
):
    import json

    log_file = tmp_path / "data_log.jsonl"

    records = [
        {
            "participant_id": "participant-1",
            "experience_id": "experience-A",
            "session_id": "session-A",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "pattern_1",
                    "questions": [
                        {
                            "question_id": "pr_q1",
                            "user_answer": "I",
                            "correct": "I",
                            "time_taken_seconds": 5,
                        }
                    ],
                }
            ],
        },
        {
            "participant_id": "participant-1",
            "experience_id": "experience-B",
            "session_id": "session-B",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "pattern_1",
                    "questions": [
                        {
                            "question_id": "pr_q1",
                            "user_answer": "H",
                            "correct": "I",
                            "time_taken_seconds": 5,
                        }
                    ],
                }
            ],
        },
    ]

    with log_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    summary = generate_experience_summary("experience-A")

    assert summary["has_data"] is True
    assert summary["experience_id"] == "experience-A"

    assert summary["total_questions"] == 1
    assert summary["objective_questions"] == 1
    assert summary["correct_objective_questions"] == 1
    assert summary["objective_accuracy"] == 1.0

    assert list(summary["sessions"]) == ["session-A"]
    assert list(summary["tasks"]) == ["pattern_recognition_v1"]
