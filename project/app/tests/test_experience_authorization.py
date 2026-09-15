from project.app.services import experience_authorization


def test_adaptive_authorization_requires_explicit_consent(
    monkeypatch,
):
    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "experience_belongs_to_participant",
        lambda experience, participant_id: True,
    )

    result = (
        experience_authorization
        .resolve_adaptive_authorization(
            "participant-1",
            "experience-1",
        )
    )

    assert result["authorized"] is True


def test_adaptive_authorization_fails_without_adaptive_consent(
    monkeypatch,
):
    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": False,
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    result = (
        experience_authorization
        .resolve_adaptive_authorization(
            "participant-1",
            "experience-1",
        )
    )

    assert result["authorized"] is False
    assert (
        result["reason"]
        == "adaptive_routing_not_authorized_by_consent"
    )


def test_adaptive_authorization_rejects_wrong_experience_owner(
    monkeypatch,
):
    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "different-participant",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "experience_belongs_to_participant",
        lambda experience, participant_id: False,
    )

    result = (
        experience_authorization
        .resolve_adaptive_authorization(
            "participant-1",
            "experience-1",
        )
    )

    assert result["authorized"] is False
    assert result["reason"] == "experience_not_owned"


def test_adaptive_authorization_rejects_bounded_experience(
    monkeypatch,
):
    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "mode": "bounded",
            "adaptive_authorized": False,
            "mode_version": "1.0",
            "authorization_source": "system",
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "experience_belongs_to_participant",
        lambda experience, participant_id: True,
    )

    result = (
        experience_authorization
        .resolve_adaptive_authorization(
            "participant-1",
            "experience-1",
        )
    )

    assert result["authorized"] is False
    assert (
        result["reason"]
        == "experience_not_in_adaptive_mode"
    )


def test_adaptive_authorization_rejects_system_source(
    monkeypatch,
):
    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant_id: {
            "participant_id": participant_id,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "system",
        },
    )

    monkeypatch.setattr(
        experience_authorization,
        "experience_belongs_to_participant",
        lambda experience, participant_id: True,
    )

    result = (
        experience_authorization
        .resolve_adaptive_authorization(
            "participant-1",
            "experience-1",
        )
    )

    assert result["authorized"] is False
    assert (
        result["reason"]
        == "invalid_adaptive_authorization_source"
    )
