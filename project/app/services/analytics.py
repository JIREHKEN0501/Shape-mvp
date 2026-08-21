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
from project.app.utils.trajectory_dynamics import (
    build_trajectory_dynamics,
)

# =========================================================
# 🧠 Canonical behavioral ontology
# =========================================================

BEHAVIOR_ONTOLOGY = {

    "processing_style": [
        "fast",
        "deliberate",
        "balanced"
    ],

    "accuracy_profile": [
        "accurate",
        "inconsistent",
        "error_prone"
    ],

    "stability_profile": [
        "stable",
        "variable"
    ],

    "confidence_profile": [
        "high_confidence",
        "moderate_confidence",
        "low_confidence"
    ]
}

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

def _extract_experience_task_attempts(
    records: List[Dict[str, Any]],
    experience_id: str,
) -> List[Dict[str, Any]]:
    """
    Extract task-completion session records belonging to one experience.

    Experience-aware task records use the session schema:
        task_id
        modules[].questions[]
        participant_id
        experience_id
        session_id
        session_complete

    This adapter normalizes those records into one attempt per question
    while preserving the experience/session boundary.
    """
    attempts: List[Dict[str, Any]] = []

    for record in records:
        if record.get("experience_id") != experience_id:
            continue

        if record.get("session_complete") is not True:
            continue

        task_id = record.get("task_id")
        participant_id = record.get("participant_id")

        if not task_id or not participant_id:
            continue

        modules = record.get("modules")

        if not isinstance(modules, list):
            continue

        for module in modules:
            if not isinstance(module, dict):
                continue

            questions = module.get("questions")

            if not isinstance(questions, list):
                continue

            for question in questions:
                if not isinstance(question, dict):
                    continue

                attempts.append(
                    {
                        "event_type": "experience_task_attempt",
                        "participant_id": participant_id,
                        "experience_id": experience_id,
                        "session_id": record.get("session_id"),
                        "task_id": task_id,
                        "ts": record.get("saved_ts") or record.get("ts"),
                        "question_id": question.get("question_id"),
                        "user_answer": question.get("user_answer"),
                        "correct": question.get("correct"),
                        "time_taken_seconds": question.get(
                            "time_taken_seconds"
                        ),
                        "module_name": module.get("module_name"),
                        "metrics": {},
                    }
                )

    return attempts

def generate_experience_summary(experience_id: str) -> Dict[str, Any]:
    """
    Generate an analytics summary bounded strictly to one experience.

    Experience-level evidence is read from completed session records
    containing the requested experience_id.

    Objective questions contribute to accuracy metrics only when a
    non-null correct answer is present. Decision/preference questions
    are preserved as observations and are not scored as correct/incorrect.
    """

    if not experience_id:
        return {
            "experience_id": experience_id,
            "has_data": False,
            "message": "experience_id_required",
        }

    all_records = _load_all_records()

    attempts = _extract_experience_task_attempts(
        all_records,
        experience_id,
    )

    if not attempts:
        return {
            "experience_id": experience_id,
            "has_data": False,
            "message": "no_records_for_experience",
        }

    objective_attempts = []
    decision_observations = []

    for index, attempt in enumerate(attempts):
        correct = attempt.get("correct")

        if correct is not None:
            attempt = dict(attempt)
            attempt["is_correct"] = (
                str(attempt.get("user_answer")).strip()
                == str(correct).strip()
            )

            attempts[index] = attempt
            objective_attempts.append(attempt)
        else:
            decision_observations.append(attempt)

    correct_attempts = sum(
        1
        for attempt in objective_attempts
        if attempt.get("is_correct") is True
    )

    objective_count = len(objective_attempts)

    accuracy = (
        correct_attempts / float(objective_count)
        if objective_count > 0
        else None
    )

    tasks = {}
    sessions = {}

    for attempt in attempts:
        task_id = attempt.get("task_id") or "unknown"
        session_id = attempt.get("session_id") or "unknown"

        task_entry = tasks.setdefault(
            task_id,
            {
                "task_id": task_id,
                "questions": 0,
                "objective_questions": 0,
                "decision_observations": 0,
                "correct": 0,
                "accuracy": None,
            },
        )

        task_entry["questions"] += 1

        if attempt.get("correct") is not None:
            task_entry["objective_questions"] += 1

            if attempt.get("is_correct") is True:
                task_entry["correct"] += 1
        else:
            task_entry["decision_observations"] += 1

        session_entry = sessions.setdefault(
            session_id,
            {
                "session_id": session_id,
                "task_id": task_id,
                "questions": 0,
            },
        )

        session_entry["questions"] += 1

    for task_entry in tasks.values():
        count = task_entry["objective_questions"]

        if count > 0:
            task_entry["accuracy"] = (
                task_entry["correct"] / float(count)
            )

    return {
        "experience_id": experience_id,
        "has_data": True,
        "total_questions": len(attempts),
        "objective_questions": len(objective_attempts),
        "decision_observations": len(decision_observations),
        "correct_objective_questions": correct_attempts,
        "objective_accuracy": accuracy,
        "tasks": tasks,
        "sessions": sessions,
        "attempts": attempts,
    }

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
    experience_id = attempt.get("experience_id")
    ts_attempt = attempt.get("ts")

    if participant_id is None or ts_attempt is None:
        return None

    best_session = None
    best_ts = None

    for sess in sessions:
        if sess.get("participant_id") != participant_id:
            continue
        if experience_id is not None:
            if sess.get("experience_id") != experience_id:
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

        hesitation = pre.get(
            "hesitation"
        )
        enriched.append(
            {
                "task_id": att.get("task_id"),
                "participant_id": att.get("participant_id"),
                "ts": att.get("ts"),
                "is_correct": is_correct,
                "category": category,
                "difficulty": difficulty,
                "response_time_s": response_time_s,
                "hesitation": hesitation,
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

def _map_pattern_to_ontology(pattern: str) -> Dict[str, str]:
    """
    Normalize freeform behavioral interpretations
    into canonical ontology terms.
    """

    p = (pattern or "").lower()

    result = {
        "processing_style": "balanced",
        "accuracy_profile": "accurate",
        "stability_profile": "stable",
        "confidence_profile": "moderate_confidence"
    }

    # -----------------------------
    # Processing style
    # -----------------------------
    if "fast" in p:
        result["processing_style"] = "fast"

    elif "deliberate" in p:
        result["processing_style"] = "deliberate"

    # -----------------------------
    # Accuracy profile
    # -----------------------------
    if "inaccurate" in p:
        result["accuracy_profile"] = "error_prone"

    elif "accurate" in p:
        result["accuracy_profile"] = "accurate"

    # -----------------------------
    # Confidence profile
    # -----------------------------
    if "confident" in p:
        result["confidence_profile"] = "high_confidence"

    elif "uncertain" in p:
        result["confidence_profile"] = "low_confidence"

    return result

def summarize_categories(cats, max_display=4):
    if len(cats) <= max_display:
        return ", ".join(cats)
    else:
        shown = ", ".join(cats[:max_display])
        remaining = len(cats) - max_display
        return f"{shown} and {remaining} more"
        
def _analyze_temporal_behavior(
    enriched_attempts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Observe behavioral trends across attempt order.

    IMPORTANT:
    This models session dynamics only.
    It does NOT infer permanent traits.
    """

    if len(enriched_attempts) < 4:
        return {
            "status": "insufficient_data"
        }

    # -----------------------------------
    # Sort chronologically
    # -----------------------------------
    attempts = sorted(
        enriched_attempts,
        key=lambda x: x.get("ts", 0)
    )

    trajectory = build_trajectory_dynamics(
        attempts
    )

    midpoint = len(attempts) // 2

    early = attempts[:midpoint]
    late = attempts[midpoint:]

    # -----------------------------------
    # Accuracy trend
    # -----------------------------------
    def accuracy(block):
        if not block:
            return 0

        correct = sum(
            1 for a in block
            if a.get("is_correct") is True
        )

        return correct / len(block)

    early_acc = accuracy(early)
    late_acc = accuracy(late)

    if late_acc > early_acc + 0.15:
        accuracy_trend = "improving"

    elif late_acc < early_acc - 0.15:
        accuracy_trend = "declining"

    else:
        accuracy_trend = "stable"

    # -----------------------------------
    # Latency trend
    # -----------------------------------
    def avg_latency(block):
        vals = [
            a.get("response_time_s")
            for a in block
            if isinstance(a.get("response_time_s"), (int, float))
        ]

        if not vals:
            return 0

        return sum(vals) / len(vals)

    early_latency = avg_latency(early)
    late_latency = avg_latency(late)

    if late_latency < early_latency * 0.8:
        latency_trend = "speeding_up"

    elif late_latency > early_latency * 1.2:
        latency_trend = "slowing_down"

    else:
        latency_trend = "stable"

    # -----------------------------------
    # Retry trend
    # -----------------------------------

    def average_effective_retries(block):
        if not block:
            return 0

        effective_retries = []

        for a in block:
            raw = a.get("raw", {})
            metrics = raw.get("metrics", {})

            retries = metrics.get("retries", 1)

            effective_retries.append(
                max(0, retries - 1)
            )

        return (
            sum(effective_retries)
            / len(effective_retries)
        )

    early_retry = average_effective_retries(early)
    late_retry = average_effective_retries(late)

    RETRY_TREND_DELTA = 0.25

    # Initial threshold.
    # Subject to validation during the
    # fatigue signal validation sprint.

    if late_retry > early_retry + RETRY_TREND_DELTA:
        retry_trend = "increasing"

    elif late_retry < early_retry - RETRY_TREND_DELTA:
        retry_trend = "decreasing"

    else:
        retry_trend = "stable"

    # -----------------------------------
    # Confidence trend
    # -----------------------------------
    retry_values = []

    for a in attempts:
        raw = a.get("raw", {})
        metrics = raw.get("metrics", {})

        retries = metrics.get("retries", 1)
        retry_values.append(retries)

    if retry_values:
        retry_variance = max(retry_values) - min(retry_values)

        if retry_variance <= 1:
            confidence_trend = "stabilizing"
        else:
            confidence_trend = "fluctuating"

    else:
        confidence_trend = "unknown"

    # -----------------------------------
    # Fatigue risk
    # -----------------------------------

    # Fatigue classifications consume only
    # independent observational signals.
    #
    # Single observations are insufficient
    # to classify fatigue.
    #
    # See:
    # - Finding 09
    # - Finding 14
    # - Finding 15
    # - Finding 16

    fatigue_risk = "low"

    # Moderate fatigue:
    # Requires corroborating evidence from
    # slowing response latency and declining accuracy.
    if (
        latency_trend == "slowing_down"
        and accuracy_trend == "declining"
    ):
        fatigue_risk = "moderate"

    # Elevated fatigue:
    # Requires an additional corroborating
    # observation (increasing retry behaviour).
    if (
        latency_trend == "slowing_down"
        and accuracy_trend == "declining"
        and retry_trend == "increasing"
    ):
        fatigue_risk = "elevated"

    return {
        "status": "ok",

        "accuracy_trend": accuracy_trend,
        "latency_trend": latency_trend,
        "retry_trend": retry_trend,
        "confidence_trend": confidence_trend,
        "fatigue_risk": fatigue_risk,
        "trajectory_shape": (
            trajectory.get(
                "trajectory_shape"
            )
        ),
        "trajectory_state": (
            trajectory.get(
                "trajectory_state"
            )
        ),
        "hesitation_trend": (
            trajectory.get(
                "hesitation_trend"
            )
        ),
        "accuracy_range": (
            trajectory.get(
                "accuracy_range"
            )
        ),
        "trajectory_note": (
            "Temporal observations describe session-level behavioral dynamics "
            "and should not be interpreted as fixed personal characteristics."
        )
    }


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

    # =========================
    # 🔥 EMERGING PATTERNS (NEW)
    # =========================

    emerging_strengths = []
    emerging_weaknesses = []

    for cat, data in by_category.items():
        attempts = data.get("attempts", 0)
        accuracy = data.get("accuracy")

        if accuracy is None:
            continue

        # lower threshold than full confidence
        if attempts >= 2:
            if accuracy >= 0.75:
                emerging_strengths.append(cat)
            elif accuracy <= 0.4:
                emerging_weaknesses.append(cat)

    # Inject into summary early (so other modules can use it later)
    summary_emerging = {
        "emerging_strengths": emerging_strengths,
        "emerging_weaknesses": emerging_weaknesses
    }

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
    
    summary.update(summary_emerging)

    # Generate explainable insights (Phase 6A)
    try:
        summary["insights"] = generate_insights(summary)

        # 🔥 EXPOSE INSIGHTS FOR FRONTEND
        ins = summary.get("insights", {})

        # High-confidence strengths only
        high_conf = [
            s["category"].replace("_", " ")
            for s in ins.get("strengths", [])
            if s.get("confidence") == "high"
        ]

        summary["strengths"] = high_conf
        summary["strengths_summary"] = summarize_categories(high_conf)

        summary["weaknesses"] = [
            g["category"].replace("_", " ")
            for g in ins.get("growth_areas", [])
        ]

        summary["patterns"] = ins.get("patterns", [])

        # =========================
        # 🧠 BEHAVIOR EXPLANATION (CLEAN + DYNAMIC)
        # =========================

        from collections import defaultdict

        pattern_groups = defaultdict(list)

        for p in summary.get("patterns", []):
            cat = p.get("category")
            if not cat:
                continue

            readable = cat.replace("_", " ")
            pattern = p.get("pattern", "").lower()

            if "confident and accurate" in pattern:
                pattern_groups["confident"].append(readable)

            elif "fast but inaccurate" in pattern:
                pattern_groups["fast"].append(readable)

            elif "deliberate and accurate" in pattern:
                pattern_groups["deliberate"].append(readable)

            elif "uncertain" in pattern:
                pattern_groups["uncertain"].append(readable)

        behavior_notes = []

        if pattern_groups["confident"]:
            behavior_notes.append(
                f"You consistently demonstrate strong confidence and accuracy across multiple domains, especially in {summarize_categories(pattern_groups['confident'])} tasks."
            )

        if pattern_groups["deliberate"]:
            behavior_notes.append(
                f"Higher accuracy was frequently observed during responses with longer response times, particularly in {summarize_categories(pattern_groups['deliberate'])} tasks."
            )

        if pattern_groups["fast"]:
            behavior_notes.append(
                f"Lower accuracy was frequently observed during faster responses in {summarize_categories(pattern_groups['fast'])} tasks."
            )

        if pattern_groups["uncertain"]:
            behavior_notes.append(
                f"There are signs of hesitation or uncertainty in {summarize_categories(pattern_groups['uncertain'])} tasks."
            )

        summary["behavior_explanation"] = behavior_notes

    except Exception:
        summary["insights"] = {
            "notes": ["Insights temporarily unavailable."]
        }

    # =========================
    # 🔥 INSIGHT AMPLIFICATION
    # =========================

    insights_text = str(summary.get("insights", ""))

    if not summary.get("insights") or "No strong patterns" in insights_text:
        if summary.get("emerging_strengths"):
            summary["insights"] = {
                "notes": [
                    f"Early strength emerging in {', '.join(summary['emerging_strengths'])} tasks."
                ]
            }

        elif summary.get("emerging_weaknesses"):
            summary["insights"] = {
                "notes": [
                    f"Early difficulty detected in {', '.join(summary['emerging_weaknesses'])} tasks."
                ]
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
    # 🧠 RESOLVED BEHAVIOR PATTERNS
    # =========================

    resolved_behavior_patterns = []

    insight_patterns = {
        p.get("category"): p.get("pattern")
        for p in summary.get("patterns", [])
    }

    category_pattern_map = {
        p.get("category"): p.get("pattern")
        for p in category_patterns
    }

    all_categories = set(
        insight_patterns.keys()
    ) | set(
        category_pattern_map.keys()
    )

    for cat in all_categories:

        insight_pattern = insight_patterns.get(cat)
        latency_pattern = category_pattern_map.get(cat)

        interpretation = None
        confidence = "moderate"

        # -----------------------------
        # Agreement
        # -----------------------------
        if insight_pattern and latency_pattern:

            if (
                "accurate" in insight_pattern.lower()
                and "accurate" in latency_pattern.lower()
            ):
                interpretation = (
                    "consistent_accuracy_behavior"
                )
                confidence = "high"

            elif (
                "fast" in latency_pattern.lower()
            ):
                interpretation = (
                    "speed_accuracy_tension"
                )

            elif (
                "deliberate" in latency_pattern.lower()
            ):
                interpretation = (
                    "deliberate_reasoning_strength"
                )

        # -----------------------------
        # Fallbacks
        # -----------------------------
        if interpretation is None:

            if latency_pattern:
                interpretation = latency_pattern

            elif insight_pattern:
                interpretation = insight_pattern

            else:
                interpretation = "unknown"

        ontology = _map_pattern_to_ontology(
            f"{insight_pattern} {latency_pattern}"
        )

        resolved_behavior_patterns.append({
            "category": cat,
            "interpretation": interpretation,

            "ontology": ontology,

            "evidence": {
                "insight_pattern": insight_pattern,
                "latency_pattern": latency_pattern,
            },

            "confidence": confidence
        })

    summary["resolved_behavior_patterns"] = (
        resolved_behavior_patterns
    )

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
                f"Lower accuracy was frequently observed alongside faster responses in {readable_cat} tasks."
            )

        elif pattern == "deliberate and accurate":
            cross_insights.append(
                f"Higher accuracy was observed alongside longer response times in {readable_cat} tasks."
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

    # =========================
    # 🧠 BEHAVIOR PROFILE
    # =========================

    behavior_profile = {
        "patterns": summary.get("patterns", []),

        "category_patterns": summary.get(
            "category_patterns", []
        ),

        "explanations": summary.get(
            "behavior_explanation", []
        ),

        "cross_domain_insights": summary.get(
            "cross_insights", []
        ),

        "behavioral_tension": summary.get(
            "behavioral_tension"
        ),

        "prediction": summary.get(
            "behavior_prediction", {}
        ),

        "strategy": {
            "consistency": summary.get("consistency"),
            "speed_style": summary.get("speed_style"),
            "stability": summary.get("stability"),
        }
    }

    summary["behavior_profile"] = behavior_profile

    # =====================================
    # ⏳ TEMPORAL BEHAVIOR OBSERVATION
    # =====================================
    try:
        summary["temporal_behavior"] = (
            _analyze_temporal_behavior(enriched)
        )

    except Exception:
        summary["temporal_behavior"] = {
            "status": "analysis_unavailable"
        }

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
