from project.app.services.experience_execution import (
    resolve_experience_execution,
)


def test_bounded_experience_cannot_execute_adaptive_consequence(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": False,
            "reason": "experience_not_in_adaptive_mode",
            "mode": {
                "mode": "bounded",
                "adaptive_authorized": False,
            },
        },
    )

    result = resolve_experience_execution(
        "participant-1",
        "experience-1",
    )

    assert result["execution_allowed"] is False
    assert result["mode"] == "bounded"
    assert result["adaptive_authorized"] is False


def test_adaptive_experience_requires_explicit_authorization(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": False,
            "reason": "adaptive_routing_not_authorized_by_consent",
            "mode": {
                "mode": "adaptive",
                "adaptive_authorized": False,
            },
        },
    )

    result = resolve_experience_execution(
        "participant-1",
        "experience-1",
    )

    assert result["execution_allowed"] is False
    assert result["mode"] == "adaptive"


def test_authorized_adaptive_experience_may_execute_consequence(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
            "reason": "explicit_adaptive_consent_and_experience_authorization",
            "mode": {
                "mode": "adaptive",
                "adaptive_authorized": True,
            },
        },
    )

    result = resolve_experience_execution(
        "participant-1",
        "experience-1",
    )

    assert result["execution_allowed"] is True
    assert result["mode"] == "adaptive"
    assert result["adaptive_authorized"] is True
    assert result["reason"] == "adaptive_execution_authorized"
