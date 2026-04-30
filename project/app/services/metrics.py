# project/app/services/metrics.py

"""
Metrics helpers for sessions.
For now, only basic behavioral metrics are implemented.
"""


def compute_behavioral_metrics(session: dict):
    """
    Very simple behavioral metrics placeholder.
    For now:
      - event_count: number of events
    """
    events = session.get("events") or []
    if not isinstance(events, list):
        events = []

    return {
        "event_count": len(events),
    }

def evaluate_task_answer(session: dict):
    """
    Evaluate a single-task result payload.

    Expects:
      - session["task_id"]
      - session["answer"]

    Looks up the task in the catalog and compares the provided
    answer to the correct answer.
    """
    task_id = session.get("task_id")
    provided = session.get("answer")

    from project.app.services.tasks import get_task  # local import to avoid cycles

    if not task_id:
        return {
            "type": "single_task",
            "valid_task": False,
            "error": "missing_task_id",
        }

    task = get_task(task_id)
    if not task:
        return {
            "type": "single_task",
            "task_id": task_id,
            "valid_task": False,
            "error": "unknown_task_id",
        }

    correct = task.get("answer")
    # compare as strings to be forgiving
    provided_str = "" if provided is None else str(provided).strip()
    correct_str = "" if correct is None else str(correct).strip()
    is_correct = bool(correct_str) and (provided_str == correct_str)

    return {
        "type": "single_task",
        "task_id": task_id,
        "valid_task": True,
        "is_correct": is_correct,
        "provided_answer": provided,
        "correct_answer": correct,
        "category": task.get("category"),
        "difficulty": task.get("difficulty"),
    }

def generate_participant_summary(participant_id: str):
    from collections import defaultdict
    import json
    import os

    log_path = "logs/data_log.jsonl"

    if not os.path.exists(log_path):
        return {
            "strengths": [],
            "weaknesses": [],
            "thinking_style": "no data"
        }

    events = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("participant_id") == participant_id:
                    events.append(entry)
            except:
                continue

    attempts = [
        e for e in events
        if e.get("event_type") == "task_attempt"
    ]

    if not attempts:
        return {
            "strengths": [],
            "weaknesses": [],
            "thinking_style": "insufficient data"
        }

    # --- CATEGORY PERFORMANCE ---
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    total_latency = 0
    total_hesitation = 0

    for ev in attempts:
        m = ev.get("metrics", {})
        cat = m.get("category", "unknown")

        category_stats[cat]["total"] += 1
        if m.get("is_correct"):
            category_stats[cat]["correct"] += 1

        total_latency += m.get("latency_ms", 0)
        total_hesitation += m.get("hesitation", 0)

    # --- ACCURACY ---
    category_accuracy = {}
    for cat, stats in category_stats.items():
        acc = stats["correct"] / stats["total"]
        category_accuracy[cat] = acc

    strengths = [cat for cat, acc in category_accuracy.items() if acc >= 0.75]
    weaknesses = [cat for cat, acc in category_accuracy.items() if acc < 0.5]

    # --- THINKING STYLE ---
    avg_latency = total_latency / len(attempts)
    avg_hesitation = total_hesitation / len(attempts)

    if avg_latency > 15000:
        style = "deliberate thinker"
    elif avg_latency < 6000 and avg_hesitation < 3:
        style = "fast and confident"
    elif avg_hesitation > 6:
        style = "hesitant / exploratory"
    else:
        style = "balanced"

    # =========================
    # 🔥 NEW: CONSISTENCY
    # =========================
    incorrect_attempts = [
        ev for ev in attempts
        if not ev.get("metrics", {}).get("is_correct")
    ]

    error_ratio = len(incorrect_attempts) / len(attempts)

    if error_ratio > 0.4:
        consistency = "low consistency"
    elif error_ratio > 0.15:
        consistency = "moderate consistency"
    else:
        consistency = "high consistency"

    # =========================
    # 🔥 NEW: SPEED vs ACCURACY
    # =========================
    if avg_latency < 6000 and error_ratio > 0.3:
        speed_style = "fast but error-prone"
    elif avg_latency > 15000 and error_ratio < 0.1:
        speed_style = "slow but highly accurate"
    elif avg_latency < 6000 and error_ratio < 0.1:
        speed_style = "fast and precise"
    else:
        speed_style = "balanced pace"

    # =========================
    # 🔥 NEW: STABILITY
    # =========================
    accuracy_values = list(category_accuracy.values())

    if accuracy_values and (max(accuracy_values) - min(accuracy_values)) > 0.5:
        stability = "uneven performance across domains"
    else:
        stability = "consistent across domains"
        
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "thinking_style": style,
        "avg_latency_ms": int(avg_latency),
        "avg_hesitation": round(avg_hesitation, 2),
        "consistency": consistency,
        "speed_style": speed_style,
        "stability": stability    
    }
