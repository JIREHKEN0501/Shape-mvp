from project.app.tasks.task_registry import TASK_SEQUENCE

from project.app.utils.experience_progression import (
    load_experience_progression,
    validate_task_progression,
)


def test_experience_created_event_contract():
    event = {
        "event": "experience_created",
        "event_version": "1.0",
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "sequence_version": "1.0",
        "ts": "2026-08-14T12:00:00Z",
    }

    assert event["event"] == "experience_created"
    assert event["event_version"] == "1.0"
    assert event["experience_id"]
    assert event["participant_id"]
    assert event["sequence_version"]
    assert event["ts"]


def test_task_completed_event_contract():
    event = {
        "event": "task_completed",
        "event_version": "1.0",
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "sequence_version": "1.0",
        "task_id": TASK_SEQUENCE[0],
        "session_id": "session-1",
        "ts": "2026-08-14T12:05:00Z",
    }

    assert event["event"] == "task_completed"
    assert event["event_version"] == "1.0"
    assert event["experience_id"]
    assert event["participant_id"]
    assert event["sequence_version"]
    assert event["task_id"]
    assert event["session_id"]
    assert event["ts"]


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
    assert event["experience_id"]
    assert event["participant_id"]
    assert event["sequence_version"]
    assert event["ts"]


def test_task_sequence_has_expected_first_task():
    assert TASK_SEQUENCE
    assert TASK_SEQUENCE[0] == "pattern_recognition_v1"


def test_new_experience_expects_first_task(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        (
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}\n'
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    state = load_experience_progression("experience-1")

    assert state["experience_id"] == "experience-1"
    assert state["participant_id"] == "participant-1"
    assert state["sequence_version"] == "1.0"
    assert state["status"] == "active"
    assert state["completed_tasks"] == []
    assert state["expected_task"] == "pattern_recognition_v1"


def test_progression_advances_after_task_completion(
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
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
        },
    )

    state = load_experience_progression("experience-1")

    assert state["status"] == "active"
    assert state["completed_tasks"] == [
        "pattern_recognition_v1"
    ]
    assert state["expected_task"] == (
        "strategy_under_constraint_v1"
    )


def test_progression_is_completed_after_final_task(
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
                '"ts":"2026-08-14T12:08:01Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    def fake_load_session(session_id):
        sessions = {
            "session-1": {
                "session_id": "session-1",
                "participant_id": "participant-1",
                "experience_id": "experience-1",
                "task_id": "pattern_recognition_v1",
            },
            "session-2": {
                "session_id": "session-2",
                "participant_id": "participant-1",
                "experience_id": "experience-1",
                "task_id": "strategy_under_constraint_v1",
            },
        }

        return sessions.get(session_id)

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        fake_load_session,
    )

    state = load_experience_progression("experience-1")

    assert state["status"] == "completed"
    assert state["completed_tasks"] == [
        "pattern_recognition_v1",
        "strategy_under_constraint_v1",
    ]
    assert state["expected_task"] is None


def test_expected_task_is_accepted(
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

    result = validate_task_progression(
        "experience-1",
        "pattern_recognition_v1",
    )

    assert result["valid"] is True
    assert result["error"] is None
    assert result["expected_task"] == "pattern_recognition_v1"


def test_out_of_order_task_is_rejected(
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

    result = validate_task_progression(
        "experience-1",
        "strategy_under_constraint_v1",
    )

    assert result["valid"] is False
    assert result["error"] == "task_not_expected"
    assert result["expected_task"] == "pattern_recognition_v1"


def test_duplicate_task_completion_is_rejected(
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
                '"task_id":"pattern_recognition_v1",'
                '"session_id":"session-2",'
                '"ts":"2026-08-14T12:06:00Z"}',
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
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
        },
    )

    result = validate_task_progression(
        "experience-1",
        "strategy_under_constraint_v1",
    )

    assert result["valid"] is False
    assert result["error"] == "invalid_progression_history"


def test_out_of_order_event_history_is_invalid(
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
                '"task_id":"strategy_under_constraint_v1",'
                '"session_id":"session-2",'
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

    result = load_experience_progression("experience-1")

    assert result["status"] == "invalid"
    assert result["error"] == "invalid_progression_history"


def test_task_completed_requires_existing_session(
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
                '"session_id":"missing-session",'
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
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: None,
    )

    result = load_experience_progression("experience-1")

    assert result["status"] == "invalid"
    assert result["error"] == "invalid_progression_history"

def test_empty_event_history_returns_not_found(
    monkeypatch,
    tmp_path,
):
    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    from project.app.utils.experience_progression import (
        load_experience_progression,
    )

    result = load_experience_progression(
        "experience-with-no-history",
    )

    assert result is None

def test_completion_event_before_all_tasks_is_invalid(
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

                '{"event":"experience_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:06:00Z"}',
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
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
        },
    )

    from project.app.utils.experience_progression import (
        load_experience_progression,
    )

    result = load_experience_progression(
        "experience-1",
    )

    assert result["status"] == "invalid"
    assert result["error"] == "invalid_progression_history"

def test_events_after_completion_make_history_invalid(
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

                '{"event":"task_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"task_id":"unexpected_task",'
                '"session_id":"session-3",'
                '"ts":"2026-08-14T12:11:00Z"}',
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

    from project.app.utils.experience_progression import (
        load_experience_progression,
    )

    result = load_experience_progression(
        "experience-1",
    )

    assert result["status"] == "invalid"
    assert result["error"] == "invalid_progression_history"

def test_duplicate_completion_events_make_history_invalid(
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

                '{"event":"experience_completed",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:11:00Z"}',
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

    from project.app.utils.experience_progression import (
        load_experience_progression,
    )

    result = load_experience_progression(
        "experience-1",
    )

    assert result["status"] == "invalid"
    assert result["error"] == "invalid_progression_history"

def test_progression_reconstruction_is_deterministic(
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
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
        },
    )

    from project.app.utils.experience_progression import (
        load_experience_progression,
    )

    first = load_experience_progression(
        "experience-1",
    )

    second = load_experience_progression(
        "experience-1",
    )

    assert first == second
