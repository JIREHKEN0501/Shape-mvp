# project/app/services/experience_progression_service.py

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from project.app.utils.experience_progression import (
    load_experience_progression,
    validate_task_progression,
)
from project.app.utils.logging import LOG_DIR
from project.app.utils.storage import save_session_result

EXPERIENCE_EVENTS_LOG = str(
    Path(LOG_DIR) / "experience_events.jsonl"
)


# One lock per experience.
#
# This prevents two submissions for the same experience
# from progressing simultaneously while allowing different
# experiences to proceed independently.
_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def _experience_lock(experience_id: str):
    """
    Return the lock associated with one experience.

    The lock registry itself is protected so that two threads
    cannot create competing locks for the same experience.
    """
    if not experience_id:
        raise ValueError("experience_id is required")

    with _LOCKS_GUARD:
        lock = _LOCKS.get(experience_id)

        if lock is None:
            lock = threading.RLock()
            _LOCKS[experience_id] = lock

        return lock


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _append_experience_event(event: dict) -> None:
    """Append one progression event to the experience event log."""
    if not isinstance(event, dict):
        raise ValueError("event must be a dict")

    Path(EXPERIENCE_EVENTS_LOG).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        EXPERIENCE_EVENTS_LOG,
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )


def complete_task_progression(
    experience_id: str,
    participant_id: str,
    session: dict,
) -> dict:
    """
    Persist a completed task session and then append the
    corresponding task_completed progression event.

    The progression read, validation, session persistence,
    and progression event append occur under the same
    per-experience lock.
    """

    if not experience_id:
        return {
            "ok": False,
            "error": "experience_id_required",
        }

    if not participant_id:
        return {
            "ok": False,
            "error": "participant_id_required",
        }

    if not isinstance(session, dict):
        return {
            "ok": False,
            "error": "session_invalid",
        }

    task_id = session.get("task_id")
    session_id = session.get("session_id")

    if not task_id:
        return {
            "ok": False,
            "error": "task_id_required",
        }

    if not session_id:
        return {
            "ok": False,
            "error": "session_id_required",
        }

    with _experience_lock(experience_id):

        progression = validate_task_progression(
            experience_id,
            task_id,
        )

        if not progression["valid"]:
            return {
                "ok": False,
                "error": progression["error"],
                "expected_task": progression.get(
                    "expected_task"
                ),
            }

        prepared_session = dict(session)

        prepared_session["participant_id"] = participant_id
        prepared_session["experience_id"] = experience_id
        prepared_session["session_complete"] = True

        try:
            saved_session = save_session_result(
                prepared_session
            )
        except Exception:
            return {
                "ok": False,
                "error": "session_persistence_failed",
            }

        event = {
            "event": "task_completed",
            "event_version": "1.0",
            "experience_id": experience_id,
            "participant_id": participant_id,
            "sequence_version": progression.get(
                "sequence_version",
                "1.0",
            ),
            "task_id": task_id,
            "session_id": saved_session.get(
                "session_id",
                session_id,
            ),
            "ts": _now_iso(),
        }

        try:
            _append_experience_event(event)
        except Exception:
            return {
                "ok": False,
                "error": "progression_event_persistence_failed",
                "session_id": saved_session.get(
                    "session_id",
                    session_id,
                ),
            }

        state = load_experience_progression(
            experience_id
        )

        if state is None:
            return {
                "ok": False,
                "error": "progression_state_unavailable",
                "session_id": saved_session.get(
                    "session_id",
                    session_id,
                ),
            }

        return {
            "ok": True,
            "session_id": saved_session.get(
                "session_id",
                session_id,
            ),
            "saved_session": saved_session,
            "task_id": task_id,
            "experience_id": experience_id,
            "event": event,
            "next_task_id": state.get("expected_task"),
            "final_task": state.get("expected_task") is None,
        }
