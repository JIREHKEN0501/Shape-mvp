from project.app.tasks.task_registry import TASK_SEQUENCE


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
