from project.app.services import adaptive_experience


def test_explicit_adaptive_consent_creates_adaptive_experience(
    monkeypatch,
):
    monkeypatch.setattr(
        adaptive_experience,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    )

    created = {
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "mode": "adaptive",
        "adaptive_authorized": True,
        "authorization_source": "consent",
    }

    monkeypatch.setattr(
        adaptive_experience,
        "create_experience",
        lambda participant_id, **kwargs: {
            **created,
            **kwargs,
        },
    )

    experience = adaptive_experience.create_authorized_adaptive_experience(
        "participant-1"
    )

    assert experience is not None
    assert experience["mode"] == "adaptive"
    assert experience["adaptive_authorized"] is True
    assert experience["authorization_source"] == "consent"


def test_general_consent_does_not_create_adaptive_experience(
    monkeypatch,
):
    monkeypatch.setattr(
        adaptive_experience,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": False,
        },
    )

    create_called = False

    def fake_create(*args, **kwargs):
        nonlocal create_called
        create_called = True
        return None

    monkeypatch.setattr(
        adaptive_experience,
        "create_experience",
        fake_create,
    )

    experience = adaptive_experience.create_authorized_adaptive_experience(
        "participant-1"
    )

    assert experience is None
    assert create_called is False


def test_missing_consent_does_not_create_adaptive_experience(
    monkeypatch,
):
    monkeypatch.setattr(
        adaptive_experience,
        "load_consent_by_participant",
        lambda participant_id: None,
    )

    create_called = False

    def fake_create(*args, **kwargs):
        nonlocal create_called
        create_called = True
        return None

    monkeypatch.setattr(
        adaptive_experience,
        "create_experience",
        fake_create,
    )

    experience = adaptive_experience.create_authorized_adaptive_experience(
        "participant-1"
    )

    assert experience is None
    assert create_called is False


def test_authorization_then_adaptive_experience_creation_uses_real_services(
    monkeypatch,
):
    from project.app.services import adaptive_authorization

    consent_record = {
        "participant_id": "participant-1",
        "consent_given": True,
        "consent_version": 1,
        "adaptive_routing_authorized": False,
    }

    monkeypatch.setattr(
        adaptive_authorization,
        "load_consent_by_participant",
        lambda participant_id: consent_record,
    )

    authorization_records = []

    monkeypatch.setattr(
        adaptive_authorization,
        "append_jsonl_secure",
        lambda path, record: (
            authorization_records.append(record) or True
        ),
    )

    assert adaptive_authorization.authorize_adaptive_routing(
        "participant-1"
    ) is True

    # The persisted authorization is now the source used by
    # the adaptive experience creation service.
    authorized_consent = {
        **consent_record,
        "adaptive_routing_authorized": True,
    }

    monkeypatch.setattr(
        adaptive_experience,
        "load_consent_by_participant",
        lambda participant_id: authorized_consent,
    )

    created = {
        "experience_id": "adaptive-experience-1",
        "participant_id": "participant-1",
        "mode": "adaptive",
        "adaptive_authorized": True,
        "authorization_source": "consent",
    }

    monkeypatch.setattr(
        adaptive_experience,
        "create_experience",
        lambda participant_id, **kwargs: {
            **created,
            **kwargs,
        },
    )

    experience = (
        adaptive_experience.create_authorized_adaptive_experience(
            "participant-1"
        )
    )

    assert len(authorization_records) == 1
    assert authorization_records[0]["adaptive_routing_authorized"] is True

    assert experience is not None
    assert experience["participant_id"] == "participant-1"
    assert experience["mode"] == "adaptive"
    assert experience["adaptive_authorized"] is True
    assert experience["authorization_source"] == "consent"
