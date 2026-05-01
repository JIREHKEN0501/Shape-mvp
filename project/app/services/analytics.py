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
from project.app.config import HESITATION_THRESHOLD
from project.app.services.metrics import evaluate_task_answer
from project.app.core.insights import generate_insights
from project.app.services.confidence import evaluate_confidence

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
        if ("task_id" in r and "answer" in r) or r.get("event_type") == "task_attempt":
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
        pre = att.get("metrics", {})
        if pre.get("is_correct") is not None:
            is_correct = pre.get("is_correct")
            category = pre.get("category")
            difficulty = pre.get("difficulty")
        else:
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
                "total_retries": 0,
                "hesitation_events": 0,
            },
        )
        entry["attempts"] += 1

        raw = att.get("raw", {})
        metrics = raw.get("metrics", {}) if raw else att.get("metrics", {})

        # Normalize retries — first click is always 1
        retries = metrics.get("retries") or 0
        effective_retries = max(0, retries - 1)
        entry["total_retries"] += effective_retries

        # Normalize hesitation — threshold filter
        hesitation = metrics.get("hesitation") or 0
        if hesitation >= HESITATION_THRESHOLD:
            entry["hesitation_events"] += 1
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
            entry["avg_retries"] = entry["total_retries"] / entry["attempts"]
            entry["hesitation_rate"] = entry["hesitation_events"] / entry["attempts"]
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

    summary = {
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

    # Generate explainable insights (Phase 6A)
    try:
        summary["insights"] = generate_insights(summary)
    except Exception:
        summary["insights"] = {
            "notes": ["Insights temporarily unavailable."]
        }

    # -----------------------------------
    # Phase 6D: Confidence & uncertainty
    # -----------------------------------
    try:
        summary["confidence"] = evaluate_confidence(summary)
    except Exception:
        summary["confidence"] = {
            "confidence_level": "unknown",
            "confidence_score": 0.0,
            "data_sufficiency": False,
            "uncertainty_factors": ["Confidence evaluation unavailable."]
        }

    # -----------------------------------
    # Phase 6E / 7A: Interpretation boundaries
    # -----------------------------------
    summary["interpretation_boundaries"] = {
        "non_diagnostic": True,
        "non_predictive": True,
        "non_deterministic": True,
        "limitations": [
            "Results reflect task performance, not intelligence, mental health, or ability.",
            "Single-session or low-volume data reduces reliability.",
            "Performance may be influenced by fatigue, context, or misunderstanding.",
            "Outputs should not be used as the sole basis for decisions affecting individuals."
        ],
        "intended_use": [
            "Self-reflection",
            "Learning support",
            "Trend monitoring over time",
            "Human-in-the-loop evaluation"
        ],
    }

    # =========================
    # 🔥 NEW: CONSISTENCY
    # =========================
    total = summary.get("total_attempts", 0)
    correct = summary.get("correct_attempts", 0)

    error_ratio = (total - correct) / total if total else 0

    if error_ratio > 0.4:
        consistency = "low consistency"
    elif error_ratio > 0.15:
        consistency = "moderate consistency"
    else:
        consistency = "high consistency"

    # =========================
    # 🔥 NEW: SPEED STYLE
    # =========================
    # use average category response time as proxy
    response_times = [
        c.get("avg_response_time_s")
        for c in summary.get("by_category", {}).values()
        if c.get("avg_response_time_s") is not None
    ]

    avg_time = sum(response_times) / len(response_times) if response_times else 0

    if avg_time < 5 and error_ratio > 0.3:
        speed_style = "fast but error-prone"
    elif avg_time > 10 and error_ratio < 0.1:
        speed_style = "slow but highly accurate"
    elif avg_time < 5 and error_ratio < 0.1:
        speed_style = "fast and precise"
    else:
        speed_style = "balanced pace"

    # =========================
    # 🔥 NEW: STABILITY
    # =========================
    acc_values = [
        c.get("accuracy")
        for c in summary.get("by_category", {}).values()
        if c.get("accuracy") is not None
    ]

    if acc_values and (max(acc_values) - min(acc_values)) > 0.5:
        stability = "uneven performance across domains"
    else:
        stability = "consistent across domains"

    # Inject into summary
    summary["consistency"] = consistency
    summary["speed_style"] = speed_style
    summary["stability"] = stability
    
    # =========================
    # 🔥 NEW: CATEGORY BEHAVIOR
    # =========================
    category_behavior = {}

    for a in enriched:
        cat = a.get("category", "unknown")

        category_behavior.setdefault(cat, {
            "fast_wrong": 0,
            "slow_correct": 0,
            "total": 0
        })

        latency = a.get("response_time_s", 0) * 1000  # convert to ms
        correct = a.get("is_correct", False)

        if latency < 6000 and not correct:
            category_behavior[cat]["fast_wrong"] += 1

        if latency > 12000 and correct:
            category_behavior[cat]["slow_correct"] += 1

        category_behavior[cat]["total"] += 1


    # --- INTERPRET CATEGORY PATTERNS ---
    category_patterns = []

    for cat, stats in category_behavior.items():
        if stats["fast_wrong"] > stats["slow_correct"]:
            pattern = "fast but inaccurate"
        elif stats["slow_correct"] > stats["fast_wrong"]:
            pattern = "deliberate and accurate"
        else:
            pattern = "balanced"

        category_patterns.append({
            "category": cat,
            "pattern": pattern
        })

    # Inject into summary
    summary["category_patterns"] = category_patterns

    # =========================
    # 🔥 CROSS-SIGNAL REASONING
    # =========================
    cross_insights = []

    for cp in category_patterns:
        cat = cp["category"]
        pattern = cp["pattern"]

        readable_cat = cat.replace("_", " ")

        if pattern == "fast but inaccurate":
            cross_insights.append(
                f"Faster responses tend to reduce accuracy in {readable_cat} tasks."
            )

        elif pattern == "deliberate and accurate":
            cross_insights.append(
                f"Taking more time improves accuracy in {readable_cat} tasks."
            )

        elif pattern == "balanced":
            continue

    # --- DETECT BEHAVIORAL TENSION ---
    fast_domains = [
        cp["category"] for cp in category_patterns
        if cp["pattern"] == "fast but inaccurate"
    ]

    behavioral_tension = None

    if fast_domains:
        readable = ", ".join([d.replace("_", " ") for d in fast_domains])
        behavioral_tension = f"Speed may be negatively impacting performance in {readable} tasks."

    summary["cross_insights"] = cross_insights

    if behavioral_tension:
        summary["behavioral_tension"] = behavioral_tension

    # =========================
    # 🔮 BEHAVIOR PREDICTION
    # =========================

    prediction = {}

    # --- Likely response style ---
    # Based on your earlier style + category patterns
    patterns = [cp["pattern"] for cp in category_patterns]

    fast_count = sum(1 for p in patterns if p == "fast but inaccurate")
    deliberate_count = sum(1 for p in patterns if p == "deliberate and accurate")

    if not patterns:
        likely_style = "adaptive"
    if deliberate_count > fast_count:
        likely_style = "deliberate"
    elif fast_count > deliberate_count:
        likely_style = "fast"
    else:
        likely_style = "adaptive"
    prediction["likely_response_style"] = likely_style


    # --- Risk under time pressure ---
    fast_inaccurate_domains = [
        cp["category"] for cp in category_patterns
        if cp["pattern"] == "fast but inaccurate"
    ]

    if fast_inaccurate_domains:
        risk = "high"
    else:
        risk = "low"

    prediction["risk_under_time_pressure"] = risk


    # --- Expected accuracy trend ---
    # Use consistency + stability signals you already compute
    consistency = summary.get("consistency", "")
    stability = summary.get("stability", "")

    if consistency and "high" in consistency and stability and "consistent" in stability:
        accuracy_trend = "stable"
    elif consistency and "low" in consistency:
        accuracy_trend = "variable"
    else:
        accuracy_trend = "moderate"
    
    prediction["expected_accuracy_trend"] = accuracy_trend


    # --- Confidence in prediction ---
    conf = summary.get("confidence", {}).get("confidence_level")

    if conf == "high":
        prediction_confidence = "high"
    else:
        prediction_confidence = "moderate"

    prediction["confidence"] = prediction_confidence

    # Inject into summary
    summary["behavior_prediction"] = prediction

    return summary


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
        if ("task_id" in r and "answer" in r) or r.get("event_type") == "task_attempt":
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
