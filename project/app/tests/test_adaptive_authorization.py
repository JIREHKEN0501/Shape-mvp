from project.app.services import adaptive_authorization


def test_adaptive_authorization_requires_existing_consent(monkeypatch):
    monkeypatch.setattr(
        adaptive_authorization,
        "load_consent_by_participant",
        lambda participant_id: None,
    )

    called = False

    def fake_append(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(
        adaptive_authorization,
        "append_jsonl_secure",
        fake_append,
    )

    assert adaptive_authorization.authorize_adaptive_routing(
        "participant-1"
    ) is False

    assert called is False


def test_adaptive_authorization_requires_consent_given(monkeypatch):
    monkeypatch.setattr(
        adaptive_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": False,
            "adaptive_routing_authorized": False,
        },
    )

    called = False

    def fake_append(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(
        adaptive_authorization,
        "append_jsonl_secure",
        fake_append,
    )

    assert adaptive_authorization.authorize_adaptive_routing(
        "participant-1"
    ) is False

    assert called is False


def test_adaptive_authorization_records_explicit_authorization(
    monkeypatch,
):
    monkeypatch.setattr(
        adaptive_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "consent_version": 1,
            "adaptive_routing_authorized": False,
        },
    )

    records = []

    monkeypatch.setattr(
        adaptive_authorization,
        "append_jsonl_secure",
        lambda path, record: (
            records.append((path, record)) or True
        ),
    )

    assert adaptive_authorization.authorize_adaptive_routing(
        "participant-1"
    ) is True

    assert len(records) == 1

    path, record = records[0]

    assert path == adaptive_authorization.CONSENT_LOG
    assert record["participant_id"] == "participant-1"
    assert record["consent_given"] is True
    assert record["adaptive_routing_authorized"] is True
    assert record["consent_version"] == 1
    assert record["timestamp"]


def test_adaptive_authorization_fails_when_persistence_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        adaptive_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "consent_version": 1,
            "adaptive_routing_authorized": False,
        },
    )

    monkeypatch.setattr(
        adaptive_authorization,
        "append_jsonl_secure",
        lambda path, record: False,
    )

    assert adaptive_authorization.authorize_adaptive_routing(
        "participant-1"
    ) is False


def test_adaptive_authorization_rejects_missing_participant():
    assert adaptive_authorization.authorize_adaptive_routing(
        ""
    ) is False

    assert adaptive_authorization.authorize_adaptive_routing(
        None
    ) is False
