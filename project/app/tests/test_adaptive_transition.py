from project.app.services.adaptive_transition import (
    execute_adaptive_transition,
)


def _authorized_experience():
    return {
        "experience_id": "experience-test",
        "participant_id": "participant-test",
        "mode": "adaptive",
        "adaptive_authorized": True,
        "mode_version": "1.0",
        "authorization_source": "consent",
    }


def test_bounded_experience_cannot_execute_transition(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": False,
            "reason": "experience_not_in_adaptive_mode",
        },
    )

    result = execute_adaptive_transition(
        "experience-test",
        "participant-test",
        "pattern_001",
        "logic_002",
    )

    assert result["ok"] is False
    assert result["error"] == "experience_not_in_adaptive_mode"


def test_wrong_transition_source_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "active",
            "sequence_version": "1.0",
            "completed_tasks": ["pattern_001"],
            "expected_task": "strategy_under_constraint_v1",
        },
    )

    result = execute_adaptive_transition(
        "experience-test",
        "participant-test",
        "wrong_source",
        "logic_002",
    )

    assert result["ok"] is False
    assert result["error"] == "invalid_adaptive_transition_source"
    assert result["expected_from_task"] == "pattern_001"


def test_ineligible_candidate_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "active",
            "sequence_version": "1.0",
            "completed_tasks": ["pattern_001"],
            "expected_task": "strategy_under_constraint_v1",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_task_eligibility",
        lambda experience_id, task_id: {
            "eligible": False,
            "reason": "already_completed",
        },
    )

    result = execute_adaptive_transition(
        "experience-test",
        "participant-test",
        "pattern_001",
        "logic_002",
    )

    assert result["ok"] is False
    assert result["error"] == "already_completed"


def test_authorized_transition_is_persisted(monkeypatch):
    events = []

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "active",
            "sequence_version": "1.0",
            "completed_tasks": ["pattern_001"],
            "expected_task": "logic_002",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_task_eligibility",
        lambda experience_id, task_id: {
            "eligible": True,
            "reason": "adaptive_task_eligible",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition._append_experience_event",
        lambda event: events.append(event),
    )

    result = execute_adaptive_transition(
        "experience-test",
        "participant-test",
        "pattern_001",
        "logic_002",
    )

    assert result["ok"] is True
    assert len(events) == 1
    assert events[0]["event"] == "adaptive_transition"
    assert events[0]["experience_id"] == "experience-test"
    assert events[0]["participant_id"] == "participant-test"
    assert events[0]["from_task_id"] == "pattern_001"
    assert events[0]["to_task_id"] == "logic_002"


def test_transition_persistence_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_authorization",
        lambda participant_id, experience_id: {
            "authorized": True,
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "active",
            "sequence_version": "1.0",
            "completed_tasks": ["pattern_001"],
            "expected_task": "logic_002",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_transition.resolve_adaptive_task_eligibility",
        lambda experience_id, task_id: {
            "eligible": True,
            "reason": "adaptive_task_eligible",
        },
    )

    def fail_append(event):
        raise OSError("write failed")

    monkeypatch.setattr(
        "project.app.services.adaptive_transition._append_experience_event",
        fail_append,
    )

    result = execute_adaptive_transition(
        "experience-test",
        "participant-test",
        "pattern_001",
        "logic_002",
    )

    assert result["ok"] is False
    assert result["error"] == "adaptive_transition_persistence_failed"
