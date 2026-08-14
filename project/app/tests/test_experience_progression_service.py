import json

from project.app.services.experience_progression_service import (
    complete_task_progression,
)


def test_complete_task_progression_persists_session_and_event(
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

    saved_sessions = []

    def fake_save_session(session):
        saved_sessions.append(dict(session))
        return dict(session)

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        fake_save_session,
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: (
            events_file.open("a", encoding="utf-8").write(
                json.dumps(event) + "\n"
            )
        ),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.load_experience_progression",
        lambda experience_id: {
            "status": "active",
            "expected_task": "strategy_under_constraint_v1",
            "sequence_version": "1.0",
        },
    )

    session = {
        "session_id": "session-1",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
    }

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True
    assert result["session_id"] == "session-1"
    assert result["task_id"] == "pattern_recognition_v1"

    assert len(saved_sessions) == 1

    with events_file.open("r", encoding="utf-8") as f:
        events = [
            json.loads(line)
            for line in f
            if line.strip()
        ]

    assert len(events) == 2

    completed_event = events[-1]

    assert completed_event["event"] == "task_completed"
    assert completed_event["experience_id"] == "experience-1"
    assert completed_event["participant_id"] == "participant-1"
    assert completed_event["task_id"] == "pattern_recognition_v1"
    assert completed_event["session_id"] == "session-1"
    assert completed_event["sequence_version"] == "1.0"
    assert completed_event["event_version"] == "1.0"


def test_task_event_is_not_written_when_session_persistence_fails(
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

    def failing_save_session(session):
        raise RuntimeError("session persistence failed")

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        failing_save_session,
    )

    event_attempts = []

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: event_attempts.append(event),
    )

    session = {
        "session_id": "session-1",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
    }

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is False
    assert result["error"] == "session_persistence_failed"

    assert event_attempts == []

def test_progression_transition_uses_experience_lock(
    monkeypatch,
):
    lock_calls = []

    class FakeLock:
        def __enter__(self):
            lock_calls.append("acquire")

        def __exit__(self, exc_type, exc, tb):
            lock_calls.append("release")

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._experience_lock",
        lambda experience_id: FakeLock(),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.validate_task_progression",
        lambda experience_id, task_id: {
            "valid": True,
            "error": None,
            "expected_task": task_id,
            "sequence_version": "1.0",
        },
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: dict(session),
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service._append_experience_event",
        lambda event: None,
    )

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.load_experience_progression",
        lambda experience_id: {
            "status": "active",
            "expected_task": "strategy_under_constraint_v1",
            "sequence_version": "1.0",
        },
    )
    session = {
        "session_id": "session-1",
        "participant_id": "participant-1",
        "experience_id": "experience-1",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
    }

    result = complete_task_progression(
        experience_id="experience-1",
        participant_id="participant-1",
        session=session,
    )

    assert result["ok"] is True
    assert lock_calls == ["acquire", "release"]
