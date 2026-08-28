from project.app.utils import experience_lifecycle


def test_create_experience_requires_participant():
    assert (
        experience_lifecycle.create_experience("")
        is None
    )


def test_create_experience_preserves_participant_identity(
    monkeypatch,
):
    records = []
    events = []

    monkeypatch.setattr(
        experience_lifecycle,
        "append_jsonl_secure",
        lambda path, record: (
            records.append((path, record)) or True
        ),
    )

    monkeypatch.setattr(
        experience_lifecycle,
        "_append_experience_event",
        lambda event: events.append(event),
    )

    result = experience_lifecycle.create_experience(
        "participant-1"
    )

    assert result is not None
    assert result["participant_id"] == "participant-1"
    assert result["experience_id"]
    assert result["experience_id"] != "participant-1"
    assert result["status"] == "active"
    assert result["sequence_version"] == "1.0"
    assert result["completed_ts"] is None

    assert len(records) == 1
    assert len(events) == 1

    assert events[0]["event"] == "experience_created"
    assert events[0]["experience_id"] == (
        result["experience_id"]
    )
    assert events[0]["participant_id"] == "participant-1"


def test_create_experience_fails_when_lifecycle_record_is_not_persisted(
    monkeypatch,
):
    events = []

    monkeypatch.setattr(
        experience_lifecycle,
        "append_jsonl_secure",
        lambda path, record: False,
    )
    monkeypatch.setattr(
        experience_lifecycle,
        "_append_experience_event",
        lambda event: events.append(event),
    )

    result = experience_lifecycle.create_experience(
        "participant-1"
    )

    assert result is None
    assert events == []


def test_complete_experience_fails_when_lifecycle_record_is_not_persisted(
    monkeypatch,
):
    active_experience = {
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "status": "active",
        "sequence_version": "1.0",
        "created_ts": "2026-08-28T12:00:00Z",
        "completed_ts": None,
    }

    monkeypatch.setattr(
        experience_lifecycle,
        "load_experience_by_id",
        lambda experience_id: active_experience,
    )
    monkeypatch.setattr(
        experience_lifecycle,
        "append_jsonl_secure",
        lambda path, record: False,
    )

    result = experience_lifecycle.complete_experience(
        "experience-1",
        "participant-1",
    )

    assert result is None
