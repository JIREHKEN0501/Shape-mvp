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
        lambda path, record: records.append(
            (path, record)
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
