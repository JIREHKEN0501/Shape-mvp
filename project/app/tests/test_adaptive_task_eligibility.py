from project.app.services.adaptive_task_eligibility import (
    resolve_adaptive_task_eligibility,
)


def test_missing_experience_id_fails_closed():
    result = resolve_adaptive_task_eligibility(
        "",
        "pattern_001",
    )

    assert result["eligible"] is False
    assert result["reason"] == "experience_id_required"


def test_missing_candidate_task_id_fails_closed():
    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "",
    )

    assert result["eligible"] is False
    assert result["reason"] == "candidate_task_id_required"


def test_unknown_experience_fails_closed(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: None,
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "pattern_001",
    )

    assert result["eligible"] is False
    assert result["reason"] == "experience_not_found"


def test_bounded_experience_cannot_execute_adaptive_task(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "bounded",
            "adaptive_authorized": False,
            "mode_version": "1.0",
            "authorization_source": "system",
        },
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "pattern_001",
    )

    assert result["eligible"] is False
    assert result["reason"] == "adaptive_execution_not_authorized"
    assert result["mode"] == "bounded"
    assert result["adaptive_authorized"] is False


def test_unauthorized_adaptive_experience_cannot_execute(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "adaptive",
            "adaptive_authorized": False,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "pattern_001",
    )

    assert result["eligible"] is False
    assert result["reason"] == "adaptive_execution_not_authorized"


def test_unknown_adaptive_task_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.list_tasks",
        lambda include_answer=False: [],
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "does_not_exist",
    )

    assert result["eligible"] is False
    assert result["reason"] == "unknown_task"


def test_completed_task_is_rejected_from_same_experience(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.list_tasks",
        lambda include_answer=False: [
            {
                "task_id": "pattern_001",
                "category": "pattern_recognition",
                "difficulty": 1,
            }
        ],
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_progression",
        lambda experience_id: {
            "completed_tasks": ["pattern_001"],
        },
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "pattern_001",
    )

    assert result["eligible"] is False
    assert result["reason"] == "already_completed"
    assert result["completed_task_ids"] == ["pattern_001"]


def test_participant_history_does_not_determine_experience_completion(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.list_tasks",
        lambda include_answer=False: [
            {
                "task_id": "pattern_001",
                "category": "pattern_recognition",
                "difficulty": 1,
            }
        ],
    )

    # The task is absent from this experience's progression.
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_progression",
        lambda experience_id: {
            "completed_tasks": [],
        },
    )

    # Deliberately provide participant-history-like data through a
    # forbidden path. The eligibility service must not consult it.
    participant_history_called = False

    def forbidden_participant_history(*args, **kwargs):
        nonlocal participant_history_called
        participant_history_called = True
        raise AssertionError(
            "Adaptive task eligibility must not consult participant history"
        )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility._load_participant_events",
        forbidden_participant_history,
        raising=False,
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "pattern_001",
    )

    assert result["eligible"] is True
    assert result["reason"] == "adaptive_task_eligible"
    assert participant_history_called is False


def test_eligible_adaptive_task_returns_candidate_identity(monkeypatch):
    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.list_tasks",
        lambda include_answer=False: [
            {
                "task_id": "logic_002",
                "category": "logical_reasoning",
                "difficulty": 2,
            }
        ],
    )

    monkeypatch.setattr(
        "project.app.services.adaptive_task_eligibility.load_experience_progression",
        lambda experience_id: {
            "completed_tasks": [],
        },
    )

    result = resolve_adaptive_task_eligibility(
        "experience-test",
        "logic_002",
    )

    assert result["eligible"] is True
    assert result["reason"] == "adaptive_task_eligible"
    assert result["experience_id"] == "experience-test"
    assert result["candidate_task_id"] == "logic_002"
