from project.app.services.adaptive_experience_execution import (
    execute_next_adaptive_task,
)


def test_bounded_experience_cannot_execute_adaptively(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": False,
            "reason": "experience_not_in_adaptive_mode",
            "mode": {
                "mode": "bounded",
                "adaptive_authorized": False,
            },
        },
    )

    result = execute_next_adaptive_task(
        participant_id="participant-1",
        experience_id="experience-1",
        from_task_id="pattern_recognition_v1",
    )

    assert result["ok"] is False
    assert result["error"] == "experience_not_in_adaptive_mode"


def test_unauthorized_adaptive_experience_cannot_execute(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": False,
            "reason": "adaptive_execution_not_authorized",
            "mode": {
                "mode": "adaptive",
                "adaptive_authorized": False,
            },
        },
    )

    result = execute_next_adaptive_task(
        participant_id="participant-1",
        experience_id="experience-1",
        from_task_id="pattern_recognition_v1",
    )

    assert result["ok"] is False
    assert result["error"] == "adaptive_execution_not_authorized"


def test_authorized_adaptive_execution_selects_checks_and_transitions(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
            "reason": "explicit_adaptive_consent_and_experience_authorization",
            "mode": {
                "mode": "adaptive",
                "adaptive_authorized": True,
            },
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.get_next_task_for_participant",
        lambda participant_id, experience_id=None: {
            "ok": True,
            "task_id": "adaptive_task_001",
            "instruction": "Test adaptive task",
            "options": ["A", "B"],
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.resolve_adaptive_task_eligibility",
        lambda experience_id, candidate_task_id: {
            "eligible": True,
            "reason": "adaptive_task_eligible",
            "experience_id": experience_id,
            "candidate_task_id": candidate_task_id,
        },
    )

    captured = {}

    def fake_transition(
        experience_id,
        participant_id,
        from_task_id,
        to_task_id,
    ):
        captured["experience_id"] = experience_id
        captured["participant_id"] = participant_id
        captured["from_task_id"] = from_task_id
        captured["to_task_id"] = to_task_id
        return {
            "ok": True,
            "event": {
                "event": "adaptive_transition",
                "from_task_id": from_task_id,
                "to_task_id": to_task_id,
            },
        }

    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.execute_adaptive_transition",
        fake_transition,
    )

    result = execute_next_adaptive_task(
        participant_id="participant-1",
        experience_id="experience-1",
        from_task_id="pattern_recognition_v1",
    )

    assert result["ok"] is True
    assert result["next_task_id"] == "adaptive_task_001"
    assert captured == {
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "from_task_id": "pattern_recognition_v1",
        "to_task_id": "adaptive_task_001",
    }


def test_adaptive_selection_failure_does_not_transition(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
            "reason": "explicit_adaptive_consent_and_experience_authorization",
            "mode": {
                "mode": "adaptive",
                "adaptive_authorized": True,
            },
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.get_next_task_for_participant",
        lambda participant_id, experience_id=None: {
            "ok": False,
            "message": "Session complete",
        },
    )

    transition_called = False

    def fail_if_called(*args, **kwargs):
        nonlocal transition_called
        transition_called = True
        return {
            "ok": True,
        }

    monkeypatch.setattr(
        "project.app.services.adaptive_experience_execution.execute_adaptive_transition",
        fail_if_called,
    )

    result = execute_next_adaptive_task(
        participant_id="participant-1",
        experience_id="experience-1",
        from_task_id="pattern_recognition_v1",
    )

    assert result["ok"] is False
    assert result["error"] == "Session complete"
    assert transition_called is False
