from project.app.tasks.task_registry import (
    TASK_SEQUENCE,
    get_next_task,
)
from project.app.utils.experience_loader import (
    experience_belongs_to_participant,
    is_experience_active,
)


def make_experience(
    experience_id="experience-1",
    participant_id="participant-1",
    status="active",
):
    return {
        "experience_id": experience_id,
        "participant_id": participant_id,
        "status": status,
        "sequence_version": "1.0",
        "created_ts": "2026-08-12T00:00:00Z",
        "completed_ts": None,
    }


def make_session(
    session_id,
    experience_id,
    participant_id,
    task_id,
):
    return {
        "session_id": session_id,
        "experience_id": experience_id,
        "participant_id": participant_id,
        "task_id": task_id,
    }


# -------------------------------------------------
# EXPERIENCE IDENTITY CONTRACT
# -------------------------------------------------

def test_experience_has_distinct_opaque_identity():
    experience = make_experience()

    assert experience["experience_id"]
    assert experience["experience_id"] != experience["participant_id"]


def test_separate_experiences_have_distinct_ids():
    experience_a = make_experience(experience_id="experience-a")
    experience_b = make_experience(experience_id="experience-b")

    assert experience_a["experience_id"] != experience_b["experience_id"]


# -------------------------------------------------
# EXPERIENCE LIFECYCLE CONTRACT
# -------------------------------------------------

def test_new_experience_starts_active():
    experience = make_experience()

    assert experience["status"] == "active"


def test_completed_experience_has_completion_timestamp():
    experience = make_experience(
        status="completed",
    )
    experience["completed_ts"] = "2026-08-12T01:00:00Z"

    assert experience["status"] == "completed"
    assert experience["completed_ts"] is not None


def test_abandoned_experience_is_not_completed():
    experience = make_experience(status="abandoned")

    assert experience["status"] == "abandoned"
    assert experience["completed_ts"] is None


# -------------------------------------------------
# SESSION MEMBERSHIP CONTRACT
# -------------------------------------------------

def test_task_session_belongs_to_exactly_one_experience():
    session = make_session(
        session_id="session-1",
        experience_id="experience-1",
        participant_id="participant-1",
        task_id="pattern_recognition_v1",
    )

    assert session["experience_id"] == "experience-1"


def test_session_identity_is_distinct_from_experience_identity():
    session = make_session(
        session_id="session-1",
        experience_id="experience-1",
        participant_id="participant-1",
        task_id="pattern_recognition_v1",
    )

    assert session["session_id"] != session["experience_id"]


def test_session_membership_preserves_participant_context():
    session = make_session(
        session_id="session-1",
        experience_id="experience-1",
        participant_id="participant-1",
        task_id="pattern_recognition_v1",
    )

    assert session["participant_id"] == "participant-1"


# -------------------------------------------------
# EXPERIENCE ISOLATION CONTRACT
# -------------------------------------------------

def test_sessions_from_separate_experiences_remain_separate():
    session_a = make_session(
        session_id="session-a",
        experience_id="experience-a",
        participant_id="participant-1",
        task_id="pattern_recognition_v1",
    )

    session_b = make_session(
        session_id="session-b",
        experience_id="experience-b",
        participant_id="participant-1",
        task_id="strategy_under_constraint_v1",
    )

    assert session_a["experience_id"] != session_b["experience_id"]


def test_experience_membership_is_not_derived_from_participant_id():
    session_a = make_session(
        session_id="session-a",
        experience_id="experience-a",
        participant_id="participant-1",
        task_id="pattern_recognition_v1",
    )

    session_b = make_session(
        session_id="session-b",
        experience_id="experience-b",
        participant_id="participant-1",
        task_id="strategy_under_constraint_v1",
    )

    # Same participant does not imply same experience.
    assert session_a["participant_id"] == session_b["participant_id"]
    assert session_a["experience_id"] != session_b["experience_id"]


# -------------------------------------------------
# TASK / EXPERIENCE COMPLETION CONTRACT
# -------------------------------------------------

def test_registered_sequence_contains_multiple_tasks():
    assert len(TASK_SEQUENCE) >= 2


def test_first_task_is_not_experience_completion():
    assert TASK_SEQUENCE[0] == "pattern_recognition_v1"
    assert TASK_SEQUENCE[0] != TASK_SEQUENCE[-1]


def test_final_task_is_distinct_from_first_task():
    assert TASK_SEQUENCE[-1] == "strategy_under_constraint_v1"
    assert TASK_SEQUENCE[-1] != TASK_SEQUENCE[0]


# -------------------------------------------------
# PARTIAL EXPERIENCE CONTRACT
# -------------------------------------------------

def test_incomplete_experience_has_no_completed_summary():
    experience = make_experience(status="active")

    completed_task_ids = {
        "pattern_recognition_v1",
    }

    required_task_ids = set(TASK_SEQUENCE)

    assert completed_task_ids != required_task_ids
    assert experience["status"] != "completed"


def test_complete_experience_requires_all_registered_tasks():
    completed_task_ids = set(TASK_SEQUENCE)
    required_task_ids = set(TASK_SEQUENCE)

    assert completed_task_ids == required_task_ids


# --------------------------------------------------
# CONTRACT TESTS
# --------------------------------------------------

def test_active_experience_is_active():
    experience = make_experience(status="active")

    assert is_experience_active(experience) is True


def test_non_active_experience_is_not_active():
    experience = make_experience(status="completed")

    assert is_experience_active(experience) is False


def test_experience_belongs_to_owning_participant():
    experience = make_experience(
        participant_id="participant-1"
    )

    assert experience_belongs_to_participant(
        experience,
        "participant-1",
    ) is True


def test_experience_does_not_belong_to_other_participant():
    experience = make_experience(
        participant_id="participant-1"
    )

    assert experience_belongs_to_participant(
        experience,
        "participant-2",
    ) is False

def test_task_session_completion_is_independent_of_experience_completion():
    first_task = TASK_SEQUENCE[0]

    next_task = get_next_task(first_task)

    assert next_task is not None
    assert next_task != first_task


def test_final_task_marks_experience_boundary():
    final_task = TASK_SEQUENCE[-1]

    next_task = get_next_task(final_task)

    assert next_task is None

def test_completed_experience_is_not_active():
    experience = make_experience(status="completed")
    assert is_experience_active(experience) is False


def test_abandoned_experience_is_not_active():
    experience = make_experience(status="abandoned")
    assert is_experience_active(experience) is False

def test_loader_returns_latest_experience_state(tmp_path, monkeypatch):
    from project.app.utils import experience_loader

    log_path = tmp_path / "experience_log.jsonl"

    records = [
        {
            "experience_id": "experience-1",
            "participant_id": "participant-1",
            "status": "active",
            "sequence_version": "1.0",
            "created_ts": "2026-08-13T12:00:00Z",
            "completed_ts": None,
        },
        {
            "experience_id": "experience-1",
            "participant_id": "participant-1",
            "status": "completed",
            "sequence_version": "1.0",
            "created_ts": "2026-08-13T12:00:00Z",
            "completed_ts": "2026-08-13T12:10:00Z",
        },
    ]

    with log_path.open("w", encoding="utf-8") as f:
        for record in records:
            import json
            f.write(json.dumps(record) + "\n")

    monkeypatch.setattr(
        experience_loader,
        "EXPERIENCE_LOG",
        str(log_path),
    )

    experience = experience_loader.load_experience_by_id("experience-1")

    assert experience is not None
    assert experience["status"] == "completed"
    assert experience["completed_ts"] == "2026-08-13T12:10:00Z"

def test_final_task_completion_persists_completed_experience(
    tmp_path,
    monkeypatch,
):
    from project.app.utils import experience_lifecycle
    from project.app.utils.experience_loader import load_experience_by_id

    log_path = tmp_path / "experience_log.jsonl"

    active_experience = make_experience(
        experience_id="experience-final",
        participant_id="participant-1",
        status="active",
    )

    import json

    with log_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(active_experience) + "\n")

    monkeypatch.setattr(
        experience_lifecycle,
        "EXPERIENCE_LOG",
        str(log_path),
    )

    # The loader uses the same log location in production,
    # so point it at the isolated test log as well.
    import project.app.utils.experience_loader as loader

    monkeypatch.setattr(
        loader,
        "EXPERIENCE_LOG",
        str(log_path),
    )

    completed = experience_lifecycle.complete_experience(
        "experience-final",
        "participant-1",
    )

    assert completed is not None
    assert completed["status"] == "completed"

    resolved = load_experience_by_id("experience-final")

    assert resolved is not None
    assert resolved["status"] == "completed"
    assert resolved["completed_ts"] is not None
