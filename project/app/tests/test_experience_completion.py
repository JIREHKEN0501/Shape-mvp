def test_experience_completed_event_contract():
    event = {
        "event": "experience_completed",
        "event_version": "1.0",
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "sequence_version": "1.0",
        "ts": "2026-08-14T12:10:00Z",
    }

    assert event["event"] == "experience_completed"
    assert event["event_version"] == "1.0"
    assert event["experience_id"] == "experience-1"
    assert event["participant_id"] == "participant-1"
    assert event["sequence_version"] == "1.0"
    assert event["ts"]

def test_final_task_appends_experience_completed_event(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:00:00Z"}',

                '{"event":"task_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"task_id":"pattern_recognition_v1",'
                '"session_id":"session-1",'
                '"ts":"2026-08-14T12:05:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": (
                "pattern_recognition_v1"
                if session_id == "session-1"
                else "strategy_under_constraint_v1"
            ),
            "session_complete": True,
        },
    )

    session = {
        "session_id": "session-3",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "strategy_under_constraint_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "allocation_round_1",
                "questions": [
                    {
                        "question_id": "suc_q1",
                        "correct": None,
                        "user_answer": "Secure immediate stability",
                        "time_taken_seconds": 5,
                    },
                    {
                        "question_id": "suc_q2",
                        "correct": None,
                        "user_answer": "Balance speed with safeguards",
                        "time_taken_seconds": 6,
                    },
                ],
            }
         ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True
    assert result["final_task"] is True

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    completion_events = [
        event
        for event in events
        if event.get("event") == "experience_completed"
    ]

    assert len(completion_events) == 1

    completed = completion_events[0]

    assert completed["event"] == "experience_completed"
    assert completed["event_version"] == "1.0"
    assert completed["experience_id"] == "experience-1"
    assert completed["participant_id"] == "participant-1"
    assert completed["sequence_version"] == "1.0"
    assert completed["ts"]

def test_duplicate_final_task_does_not_append_second_completion_event(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:00:00Z"}',

                '{"event":"task_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"task_id":"pattern_recognition_v1",'
                '"session_id":"session-1",'
                '"ts":"2026-08-14T12:05:00Z"}',

                '{"event":"task_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"task_id":"strategy_under_constraint_v1",'
                '"session_id":"session-2",'
                '"ts":"2026-08-14T12:08:00Z"}',

                '{"event":"experience_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:10:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    session = {
        "session_id": "session-3",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "strategy_under_constraint_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "allocation_round_1",
                "questions": [
                    {
                        "question_id": "suc_q1",
                        "correct": None,
                        "user_answer": "Secure immediate stability",
                        "time_taken_seconds": 5,
                    },
                    {
                        "question_id": "suc_q2",
                        "correct": None,
                        "user_answer": "Balance speed with safeguards",
                        "time_taken_seconds": 6,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is False

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    completion_events = [
        event
        for event in events
        if event.get("event") == "experience_completed"
    ]

    assert len(completion_events) == 1

def test_experience_cannot_complete_before_all_tasks(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:00:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
        },
    )

    session = {
        "session_id": "session-2",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "pattern_1",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "correct": "I",
                        "user_answer": "I",
                        "time_taken_seconds": 4,
                    },
                    {
                        "question_id": "pr_q2",
                        "correct": "30",
                        "user_answer": "30",
                        "time_taken_seconds": 5,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True
    assert result["final_task"] is False

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    completion_events = [
        event
        for event in events
        if event.get("event") == "experience_completed"
    ]

    assert completion_events == []

def test_completion_event_failure_does_not_report_completed(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:00:00Z"}',

                '{"event":"task_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"task_id":"pattern_recognition_v1",'
                '"session_id":"session-1",'
                '"ts":"2026-08-14T12:05:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    def failing_completion_event(event):
        if event.get("event") == "experience_completed":
            raise RuntimeError("completion event write failed")

        with events_file.open("a", encoding="utf-8") as f:
            f.write(__import__("json").dumps(event) + "\n")

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        failing_completion_event,
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": (
                "pattern_recognition_v1"
                if session_id == "session-1"
                else "strategy_under_constraint_v1"
            ),
            "session_complete": True,
        },
    )

    session = {
        "session_id": "session-2",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "strategy_under_constraint_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "allocation_round_1",
                "questions": [
                    {
                        "question_id": "suc_q1",
                        "correct": None,
                        "user_answer": "Secure immediate stability",
                        "time_taken_seconds": 5,
                    },
                    {
                        "question_id": "suc_q2",
                        "correct": None,
                        "user_answer": "Balance speed with safeguards",
                        "time_taken_seconds": 6,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is False
    assert result["error"] == "completion_event_persistence_failed"

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    completion_events = [
        event
        for event in events
        if event.get("event") == "experience_completed"
    ]

    assert completion_events == []

def test_incomplete_session_does_not_advance_progression(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-17T09:00:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    session = {
        "session_id": "session-incomplete",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": False,
        "modules": [
            {
                "module_name": "pattern_1",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "correct": "I",
                        "user_answer": None,
                        "time_taken_seconds": 4,
                    },
                    {
                        "question_id": "pr_q2",
                        "correct": "30",
                        "user_answer": None,
                        "time_taken_seconds": 5,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is False

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    task_completed_events = [
        event
        for event in events
        if event.get("event") == "task_completed"
    ]

    assert task_completed_events == []

def test_claimed_completion_without_required_evidence_does_not_advance_progression(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-17T09:00:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    session = {
        "session_id": "session-incomplete-evidence",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "pattern_1",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "correct": "I",
                        "user_answer": None,
                        "time_taken_seconds": 4,
                    },
                    {
                        "question_id": "pr_q2",
                        "correct": "30",
                        "user_answer": None,
                        "time_taken_seconds": 5,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is False

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    task_completed_events = [
        event
        for event in events
        if event.get("event") == "task_completed"
    ]

    assert task_completed_events == []

def test_valid_completed_task_advances_progression(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-17T09:00:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
        },
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                __import__("json").dumps(event) + "\n"
            )
        ),
    )

    session = {
        "session_id": "session-complete",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "pattern_1",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "correct": "I",
                        "user_answer": "I",
                        "time_taken_seconds": 4,
                    },
                    {
                        "question_id": "pr_q2",
                        "correct": "30",
                        "user_answer": "30",
                        "time_taken_seconds": 5,
                    },
                ],
            }
        ],
    }

    from project.app.services.experience_progression_service import (
        complete_task_progression,
    )

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True
    assert result["final_task"] is False

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            __import__("json").loads(line)
            for line in f
            if line.strip()
        ]

    task_completed_events = [
        event
        for event in events
        if event.get("event") == "task_completed"
    ]

    assert len(task_completed_events) == 1

    completed = task_completed_events[0]

    assert completed["task_id"] == "pattern_recognition_v1"
    assert completed["session_id"] == "session-complete"

def _write_experience_analytics_records(path):
    import json

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
                            "user_answer": "32",
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
                            "time_taken_seconds": 10,
                        },
                        {
                            "question_id": "suc_q2",
                            "user_answer": "Balance speed with safeguards",
                            "correct": None,
                            "time_taken_seconds": 11,
                        },
                    ],
                }
            ],
        },
        {
            "participant_id": "participant-1",
            "experience_id": "experience-2",
            "session_id": "session-3",
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
                        },
                        {
                            "question_id": "pr_q2",
                            "user_answer": "30",
                            "correct": "30",
                            "time_taken_seconds": 5,
                        },
                    ],
                }
            ],
        },
    ]

    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record) + "\n")


def test_experience_summary_isolation_and_session_boundary(
    monkeypatch,
    tmp_path,
):
    from project.app.services import analytics

    data_log = tmp_path / "data_log.jsonl"
    _write_experience_analytics_records(data_log)

    monkeypatch.setattr(
        analytics,
        "DATA_LOG",
        str(data_log),
    )

    summary = analytics.generate_experience_summary("experience-1")

    assert summary["has_data"] is True
    assert summary["experience_id"] == "experience-1"
    assert summary["total_questions"] == 4

    assert set(summary["sessions"]) == {
        "session-1",
        "session-2",
    }

    assert "session-3" not in summary["sessions"]


def test_experience_summary_scores_only_objective_questions(
    monkeypatch,
    tmp_path,
):
    from project.app.services import analytics

    data_log = tmp_path / "data_log.jsonl"
    _write_experience_analytics_records(data_log)

    monkeypatch.setattr(
        analytics,
        "DATA_LOG",
        str(data_log),
    )

    summary = analytics.generate_experience_summary("experience-1")

    assert summary["objective_questions"] == 2
    assert summary["correct_objective_questions"] == 1
    assert summary["objective_accuracy"] == 0.5


def test_experience_summary_preserves_decision_observations(
    monkeypatch,
    tmp_path,
):
    from project.app.services import analytics

    data_log = tmp_path / "data_log.jsonl"
    _write_experience_analytics_records(data_log)

    monkeypatch.setattr(
        analytics,
        "DATA_LOG",
        str(data_log),
    )

    summary = analytics.generate_experience_summary("experience-1")

    assert summary["decision_observations"] == 2

    strategy = summary["tasks"]["strategy_under_constraint_v1"]

    assert strategy["questions"] == 2
    assert strategy["objective_questions"] == 0
    assert strategy["decision_observations"] == 2
    assert strategy["correct"] == 0
    assert strategy["accuracy"] is None


def test_experience_summary_excludes_incomplete_sessions(
    monkeypatch,
    tmp_path,
):
    from project.app.services import analytics

    data_log = tmp_path / "data_log.jsonl"

    _write_experience_analytics_records(data_log)

    with data_log.open("a", encoding="utf-8") as fh:
        import json

        fh.write(
            json.dumps(
                {
                    "participant_id": "participant-1",
                    "experience_id": "experience-1",
                    "session_id": "session-incomplete",
                    "task_id": "pattern_recognition_v1",
                    "session_complete": False,
                    "modules": [
                        {
                            "module_name": "pattern_1",
                            "questions": [
                                {
                                    "question_id": "pr_q1",
                                    "user_answer": "I",
                                    "correct": "I",
                                    "time_taken_seconds": 3,
                                }
                            ],
                        }
                    ],
                }
            )
            + "\n"
        )

    monkeypatch.setattr(
        analytics,
        "DATA_LOG",
        str(data_log),
    )

    summary = analytics.generate_experience_summary("experience-1")

    assert summary["total_questions"] == 4
    assert "session-incomplete" not in summary["sessions"]
