# project/app/services/analytics.py

"""
Analytics helpers for participant performance and usage.

We operate mainly on logs/data_log.jsonl and use:
- session_start records (event_type == "session_start")
- single-task submission records (with "task_id" and "answer")

We re-use the evaluate_task_answer() logic so scoring stays consistent.
"""

import json
import os
from typing import List, Dict, Any, Optional

from project.app.helpers import DATA_LOG
from project.app.services.metrics import evaluate_task_answer


def _load_all_records() -> List[Dict[str, Any]]:
    """
    Load all records from the main data log.

    Returns an empty list if the log file does not exist or is unreadable.
    """
    if not os.path.exists(DATA_LOG):
        return []

    records: List[Dict[str, Any]] = []
    with open(DATA_LOG, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    records.append(obj)
            except Exception:
                # skip malformed lines
                continue
    return records


def _filter_by_participant(records: List[Dict[str, Any]], participant_id: str) -> List[Dict[str, Any]]:
    """
    Filter all records for a given participant_id.
    """
    return [r for r in records if r.get("participant_id") == participant_id]


def _extract_sessions(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract session_start records from a set of records.
    """
    return [r for r in records if r.get("event_type") == "session_start"]


def _extract_task_attempts(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract single-task submission records.

    We treat any record that has:
      - a "task_id"
      - an "answer"
    as a single-task attempt.
    """
    attempts: List[Dict[str, Any]] = []
    for r in records:
        if "task_id" in r and "answer" in r:
            attempts.append(r)
    return attempts


def _match_session_for_attempt(
    attempt: Dict[str, Any],
    sessions: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Find the most recent session_start for the same participant (and task_id, if present)
    that happened at or before the attempt timestamp.

    This is used to compute response time.
    """
    participant_id = attempt.get("participant_id")
    task_id = attempt.get("task_id")
    ts_attempt = attempt.get("ts")

    if participant_id is None or ts_attempt is None:
        return None

    best_session = None
    best_ts = None

    for sess in sessions:
        if sess.get("participant_id") != participant_id:
            continue

        ts_sess = sess.get("ts")
        if ts_sess is None or ts_sess > ts_attempt:
            # session after attempt, ignore
            continue

        # If the session has a task_id, and this attempt has a task_id,
        # prefer sessions with matching task_id.
        sess_task_id = sess.get("task_id")
        if task_id and sess_task_id and sess_task_id != task_id:
            continue

        if best_ts is None or ts_sess > best_ts:
            best_ts = ts_sess
            best_session = sess

    return best_session


def _augment_attempts_with_metrics_and_time(
    attempts: List[Dict[str, Any]],
    sessions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    For each attempt, compute:
      - is_correct, category, difficulty (via evaluate_task_answer)
      - response_time_s (if we can match to a session_start)
    """
    enriched: List[Dict[str, Any]] = []

    for att in attempts:
        metrics = evaluate_task_answer(att)
        is_correct = metrics.get("is_correct")
        category = metrics.get("category")
        difficulty = metrics.get("difficulty")

        # compute response time from nearest session_start
        sess = _match_session_for_attempt(att, sessions)
        response_time_s = None
        if sess is not None:
            ts_attempt = att.get("ts")
            ts_sess = sess.get("ts")
            if isinstance(ts_attempt, (int, float)) and isinstance(ts_sess, (int, float)):
                response_time_s = max(0.0, float(ts_attempt) - float(ts_sess))

        enriched.append(
            {
                "task_id": att.get("task_id"),
                "participant_id": att.get("participant_id"),
                "ts": att.get("ts"),
                "is_correct": is_correct,
                "category": category,
                "difficulty": difficulty,
                "response_time_s": response_time_s,
                "raw": att,
            }
        )

    return enriched


def _aggregate_by_task(enriched_attempts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate attempts by task_id.
    """
    by_task: Dict[str, Dict[str, Any]] = {}

    for att in enriched_attempts:
        task_id = att.get("task_id") or "unknown"
        entry = by_task.setdefault(
            task_id,
            {
                "task_id": task_id,
                "attempts": 0,
                "correct": 0,
                "wrong": 0,
                "last_ts": None,
                "avg_response_time_s": None,
            },
        )
        entry["attempts"] += 1
        if att.get("is_correct") is True:
            entry["correct"] += 1
        else:
            entry["wrong"] += 1

        ts = att.get("ts")
        if ts is not None:
            if entry["last_ts"] is None or ts > entry["last_ts"]:
                entry["last_ts"] = ts

        rt = att.get("response_time_s")
        if rt is not None:
            if "response_times" not in entry:
                entry["response_times"] = []
            entry["response_times"].append(rt)

    # finalize averages
    for task_id, entry in by_task.items():
        rts = entry.get("response_times") or []
        if rts:
            entry["avg_response_time_s"] = sum(rts) / len(rts)
        entry.pop("response_times", None)

        if entry["attempts"] > 0:
            entry["accuracy"] = entry["correct"] / float(entry["attempts"])
        else:
            entry["accuracy"] = None

    return by_task


def _aggregate_by_category(enriched_attempts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate attempts by task category.
    """
    by_cat: Dict[str, Dict[str, Any]] = {}

    for att in enriched_attempts:
        category = att.get("category") or "unknown"
        entry = by_cat.setdefault(
            category,
            {
                "category": category,
                "attempts": 0,
                "correct": 0,
                "wrong": 0,
                "avg_response_time_s": None,
            },
        )
        entry["attempts"] += 1
        if att.get("is_correct") is True:
            entry["correct"] += 1
        else:
            entry["wrong"] += 1

        rt = att.get("response_time_s")
        if rt is not None:
            if "response_times" not in entry:
                entry["response_times"] = []
            entry["response_times"].append(rt)

    # finalize
    for cat, entry in by_cat.items():
        rts = entry.get("response_times") or []
        if rts:
            entry["avg_response_time_s"] = sum(rts) / len(rts)
        entry.pop("response_times", None)

        if entry["attempts"] > 0:
            entry["accuracy"] = entry["correct"] / float(entry["attempts"])
        else:
            entry["accuracy"] = None

    return by_cat


def generate_participant_summary(participant_id: str) -> Dict[str, Any]:
    """
    Compute a detailed summary for a single participant.
    """
    all_records = _load_all_records()
    if not all_records:
        return {
            "participant_id": participant_id,
            "has_data": False,
            "message": "no_data_log",
        }

    records = _filter_by_participant(all_records, participant_id)
    if not records:
        return {
            "participant_id": participant_id,
            "has_data": False,
            "message": "no_records_for_participant",
        }

    sessions = _extract_sessions(records)
    attempts = _extract_task_attempts(records)
    enriched = _augment_attempts_with_metrics_and_time(attempts, sessions)

    total_attempts = len(enriched)
    correct_attempts = sum(1 for a in enriched if a.get("is_correct") is True)
    wrong_attempts = total_attempts - correct_attempts
    accuracy = correct_attempts / float(total_attempts) if total_attempts > 0 else None

    by_task = _aggregate_by_task(enriched)
    by_category = _aggregate_by_category(enriched)

    # activity window
    all_ts = [r.get("ts") for r in records if isinstance(r.get("ts"), (int, float))]
    first_ts = min(all_ts) if all_ts else None
    last_ts = max(all_ts) if all_ts else None

    return {
        "participant_id": participant_id,
        "has_data": True,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "wrong_attempts": wrong_attempts,
        "accuracy": accuracy,
        "by_task": by_task,
        "by_category": by_category,
        "first_activity_ts": first_ts,
        "last_activity_ts": last_ts,
        "sessions_count": len(sessions),
    }


def generate_global_summary() -> Dict[str, Any]:
    """
    Compute a coarse global summary across all participants.
    """
    all_records = _load_all_records()
    if not all_records:
        return {
            "has_data": False,
            "message": "no_data_log",
        }

    # map participant_id -> enriched attempts
    per_participant_attempts: Dict[str, List[Dict[str, Any]]] = {}
    for r in all_records:
        pid = r.get("participant_id")
        if not pid:
            continue
        # we only extract single-task attempts here
        if "task_id" in r and "answer" in r:
            per_participant_attempts.setdefault(pid, []).append(r)

    # compute per-participant accuracy
    participant_summaries: Dict[str, Dict[str, Any]] = {}
    all_enriched: List[Dict[str, Any]] = []
    for pid, attempts in per_participant_attempts.items():
        # we don't need sessions here for global accuracy,
        # only correctness and category/difficulty.
        enriched = _augment_attempts_with_metrics_and_time(attempts, sessions=[])
        all_enriched.extend(enriched)

        total = len(enriched)
        correct = sum(1 for a in enriched if a.get("is_correct") is True)
        acc = correct / float(total) if total > 0 else None
        participant_summaries[pid] = {
            "participant_id": pid,
            "attempts": total,
            "correct": correct,
            "accuracy": acc,
        }

    # aggregate globally
    total_attempts = len(all_enriched)
    correct_attempts = sum(1 for a in all_enriched if a.get("is_correct") is True)
    wrong_attempts = total_attempts - correct_attempts
    accuracy = correct_attempts / float(total_attempts) if total_attempts > 0 else None

    # aggregate tasks
    by_task = _aggregate_by_task(all_enriched)
    # quick "most attempted" list
    most_attempted = sorted(by_task.values(), key=lambda e: e["attempts"], reverse=True)

    # global by category
    by_category = _aggregate_by_category(all_enriched)

    return {
        "has_data": True,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "wrong_attempts": wrong_attempts,
        "accuracy": accuracy,
        "participants": participant_summaries,
        "by_task": by_task,
        "by_category": by_category,
        "most_attempted_tasks": most_attempted[:5],
    }

