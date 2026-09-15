from project.app.services.tasks import (
    _get_experience_task_exclusion,
    get_next_task_for_participant,
)

def test_experience_exclusion_reads_progression_not_participant_history(
    monkeypatch,
):
    participant_id = "participant-test"
    experience_id = "experience-test"

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": participant_id,
            "status": "active",
            "completed_tasks": [],
            "expected_task": "logic_002",
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        experience_id,
        participant_id,
    )

    assert error is None
    assert completed_tasks == set()


def test_experience_completed_task_is_used_for_exclusion(
    monkeypatch,
):
    participant_id = "participant-test"
    experience_id = "experience-test"

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": participant_id,
            "status": "active",
            "completed_tasks": [
                "pattern_001",
                "logic_002",
            ],
            "expected_task": "memory_001",
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        experience_id,
        participant_id,
    )

    assert error is None
    assert completed_tasks == {
        "pattern_001",
        "logic_002",
    }


def test_task_completed_in_another_experience_is_not_excluded(
    monkeypatch,
):
    participant_id = "participant-test"
    experience_id = "experience-test"

    # This represents the authoritative state of THIS experience.
    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": participant_id,
            "status": "active",
            "completed_tasks": [],
            "expected_task": "pattern_001",
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        experience_id,
        participant_id,
    )

    assert error is None
    assert "pattern_001" not in completed_tasks


def test_wrong_owner_fails_closed(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "different-participant",
            "status": "active",
            "completed_tasks": [],
            "expected_task": "pattern_001",
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        "experience-test",
        "participant-test",
    )

    assert completed_tasks is None
    assert error == "experience_not_owned"


def test_invalid_progression_fails_closed(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "invalid",
            "completed_tasks": [],
            "expected_task": None,
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        "experience-test",
        "participant-test",
    )

    assert completed_tasks is None
    assert error == "invalid_progression_history"


def test_missing_experience_fails_closed(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: None,
    )

    completed_tasks, error = _get_experience_task_exclusion(
        "experience-test",
        "participant-test",
    )

    assert completed_tasks is None
    assert error == "experience_not_found"


def test_malformed_completed_tasks_fail_closed(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_experience_progression",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-test",
            "status": "active",
            "completed_tasks": "not-a-list",
            "expected_task": "pattern_001",
            "sequence_version": "1.0",
        },
    )

    completed_tasks, error = _get_experience_task_exclusion(
        "experience-test",
        "participant-test",
    )

    assert completed_tasks is None
    assert error == "invalid_progression_history"


def test_missing_experience_id_fails_closed():
    completed_tasks, error = _get_experience_task_exclusion(
        "",
        "participant-test",
    )

    assert completed_tasks is None
    assert error == "experience_id_required"

def test_adaptive_selector_uses_experience_scoped_exclusion(
    monkeypatch,
):
    participant_id = "participant-test"
    experience_id = "experience-test"

    captured = {}

    def fake_exclusion(experience_id_arg, participant_id_arg):
        captured["experience_id"] = experience_id_arg
        captured["participant_id"] = participant_id_arg
        return {"already_completed_in_experience"}, None

    monkeypatch.setattr(
        "project.app.services.tasks._get_experience_task_exclusion",
        fake_exclusion,
    )

    monkeypatch.setattr(
        "project.app.services.tasks._load_participant_events",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        "project.app.services.tasks._summarise_history",
        lambda events: {
            "attempted_task_ids": {"participant_history_task"},
            "attempts_by_category": {},
            "correct_by_category": {},
            "difficulties_by_category": {},
        },
    )

    def stop_after_exclusion(*args, **kwargs):
        raise AssertionError(
            "Selector continued after establishing exclusion set"
        )

    monkeypatch.setattr(
        "project.app.services.tasks.generate_participant_summary",
        stop_after_exclusion,
    )

    try:
        get_next_task_for_participant(
            participant_id,
            experience_id=experience_id,
        )
    except AssertionError as exc:
        assert str(exc) == (
            "Selector continued after establishing exclusion set"
        )
    else:
        raise AssertionError(
            "Expected selector to continue into routing"
        )

    assert captured == {
        "experience_id": experience_id,
        "participant_id": participant_id,
    }
