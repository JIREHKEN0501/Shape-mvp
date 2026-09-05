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

def test_experience_summary_builds_server_resolved_strategy_decisions(
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

    strategy = summary["strategy"]
    decisions = strategy["decisions"]

    assert len(decisions) == 2

    assert decisions[0] == {
        "question_id": "suc_q1",
        "selected_option": "Secure immediate stability",
        "decision_code": "stability_first",
        "time_taken_seconds": 19,
    }

    assert decisions[1] == {
        "question_id": "suc_q2",
        "selected_option": "Balance speed with safeguards",
        "decision_code": "balanced_safeguards",
        "time_taken_seconds": 20,
    }

    # The raw participant observations remain untouched.
    assert all(
        "decision_code" not in attempt
        for attempt in summary["attempts"]
    )

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

def test_completed_task_persistence_is_consumable_by_experience_summary(
    monkeypatch,
    tmp_path,
):
    import json

    log_file = tmp_path / "data_log.jsonl"
    experience_events_file = tmp_path / "experience_events.jsonl"

    experience_events_file.write_text(
        json.dumps(
            {
                "event": "experience_created",
                "event_version": "1.0",
                "experience_id": "experience-regression-1",
                "participant_id": "participant-1",
                "sequence_version": "1.0",
                "ts": "2026-08-21T12:00:00Z",
            }
        ) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(experience_events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.EXPERIENCE_EVENTS_LOG",
        str(experience_events_file),
    )

    persisted = []

    def fake_save_session_result(session):
        saved = dict(session)
        persisted.append(saved)

        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(saved) + "\n")

        return saved

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        fake_save_session_result,
    )

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    session = {
        "session_id": "session-regression-1",
        "participant_id": "participant-1",
        "experience_id": "experience-regression-1",
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
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-regression-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True

    assert len(persisted) == 1

    saved = persisted[0]

    assert saved["participant_id"] == "participant-1"
    assert saved["experience_id"] == "experience-regression-1"
    assert saved["session_id"] == "session-regression-1"
    assert saved["task_id"] == "pattern_recognition_v1"
    assert saved["session_complete"] is True

    summary = generate_experience_summary(
        "experience-regression-1"
    )

    assert summary["has_data"] is True
    assert summary["experience_id"] == "experience-regression-1"
    assert summary["total_questions"] == 2
    assert summary["objective_questions"] == 2
    assert summary["correct_objective_questions"] == 2
    assert summary["objective_accuracy"] == 1.0
    assert list(summary["sessions"]) == [
        "session-regression-1"
    ]

def test_participant_submission_persists_completed_session_for_experience_analytics(
    monkeypatch,
    tmp_path,
):
    import json

    from project.app import create_app

    log_file = tmp_path / "data_log.jsonl"
    experience_events_file = tmp_path / "experience_events.jsonl"

    experience_events_file.write_text(
        json.dumps(
            {
                "event": "experience_created",
                "event_version": "1.0",
                "experience_id": "experience-route-regression",
                "participant_id": "participant-route-1",
                "sequence_version": "1.0",
                "ts": "2026-08-21T12:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(log_file),
    )

    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG",
        str(log_file),
    )
    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG_PATH",
        log_file,
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.EXPERIENCE_EVENTS_LOG",
        str(experience_events_file),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(experience_events_file),
    )

    # We will replace the actual experience lookup with a valid
    # in-memory experience belonging to the participant.
    experience = {
        "experience_id": "experience-route-regression",
        "participant_id": "participant-route-1",
        "status": "active",
    }

    monkeypatch.setattr(
        "project.app.routes.participant.load_experience_by_id",
        lambda experience_id: (
            experience
            if experience_id == "experience-route-regression"
            else None
        ),
    )

    monkeypatch.setattr(
        "project.app.routes.participant.experience_belongs_to_participant",
        lambda loaded_experience, participant_id: (
            loaded_experience.get("participant_id") == participant_id
        ),
    )

    monkeypatch.setattr(
        "project.app.routes.participant.is_experience_active",
        lambda loaded_experience: True,
    )

    app = create_app({"TESTING": True})
    app.config["TESTING"] = True

    client = app.test_client()

    client.set_cookie("participant_id", "participant-route-1")
    client.set_cookie("experience_id", "experience-route-regression")

    response = client.post(
        "/participant/submit_result",
        json={
            "task_id": "pattern_recognition_v1",
            "session_id": "route-regression-session-1",
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
            "session_complete": True,
        },
    )

    assert response.status_code == 201, response.get_json()

    payload = response.get_json()

    assert payload["session_complete"] is True
    assert payload["saved"]["participant_id"] == "participant-route-1"
    assert payload["saved"]["experience_id"] == "experience-route-regression"
    assert payload["saved"]["task_id"] == "pattern_recognition_v1"
    assert payload["experience_complete"] is False
    assert payload["next_task_id"] == "strategy_under_constraint_v1"

    assert log_file.exists()

    records = [
        json.loads(line)
        for line in log_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    completed = [
        record
        for record in records
        if record.get("session_id") == "route-regression-session-1"
    ]

    assert len(completed) == 1

    persisted = completed[0]

    assert persisted["session_complete"] is True
    assert persisted["experience_id"] == "experience-route-regression"
    assert persisted["participant_id"] == "participant-route-1"

    from project.app.services.analytics import generate_experience_summary

    summary = generate_experience_summary(
        "experience-route-regression"
    )

    assert summary["has_data"] is True
    assert summary["experience_id"] == "experience-route-regression"
    assert summary["total_questions"] == 2
    assert summary["objective_questions"] == 2
    assert summary["correct_objective_questions"] == 2
    assert summary["objective_accuracy"] == 1.0

def test_experience_strategy_decisions_are_isolated_by_experience(
    monkeypatch,
    tmp_path,
):
    log_file = tmp_path / "data_log.jsonl"

    records = [
        {
            "participant_id": "participant-1",
            "experience_id": "experience-A",
            "session_id": "session-A",
            "task_id": "strategy_under_constraint_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "allocation_round_1",
                    "questions": [
                        {
                            "question_id": "suc_q1",
                            "user_answer": "Secure immediate stability",
                            "time_taken_seconds": 10,
                        }
                    ],
                }
            ],
        },
        {
            "participant_id": "participant-1",
            "experience_id": "experience-B",
            "session_id": "session-B",
            "task_id": "strategy_under_constraint_v1",
            "session_complete": True,
            "modules": [
                {
                    "module_name": "allocation_round_1",
                    "questions": [
                        {
                            "question_id": "suc_q1",
                            "user_answer": "Invest in long-term payoff",
                            "time_taken_seconds": 12,
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

    summary_a = generate_experience_summary("experience-A")
    summary_b = generate_experience_summary("experience-B")

    assert summary_a["strategy"]["decisions"] == [
        {
            "question_id": "suc_q1",
            "selected_option": "Secure immediate stability",
            "decision_code": "stability_first",
            "time_taken_seconds": 10,
        }
    ]

    assert summary_b["strategy"]["decisions"] == [
        {
            "question_id": "suc_q1",
            "selected_option": "Invest in long-term payoff",
            "decision_code": "long_term_payoff",
            "time_taken_seconds": 12,
        }
    ]
