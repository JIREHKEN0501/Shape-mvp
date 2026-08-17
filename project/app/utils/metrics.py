# project/app/utils/metrics.py

import math

def compute_behavioral_metrics(session: dict) -> dict:
    """
    Compute metrics from behavioral sessions.
    Session structure:
    {
        "participant_id": "...",
        "task_id": "...",
        "start_ts": <ms>,
        "end_ts": <ms>,
        "events": [
            {"type": "...", "ts": <ms>},
            ...
        ]
    }
    """
    events = session.get("events", [])
    start = session.get("start_ts")
    end = session.get("end_ts")

    total_ms = max(0, (end - start)) if (start and end) else None
    hints = sum(1 for e in events if e.get("type") == "hint")
    retries = sum(1 for e in events if e.get("type") == "retry")

    timestamps = sorted([e.get("ts") for e in events if isinstance(e.get("ts"), (int, float))])
    hesitation_ms = 0
    for a, b in zip(timestamps, timestamps[1:]):
        if b - a > 1500:
            hesitation_ms += (b - a)

    # simple score model
    score = 100
    if total_ms is not None:
        score -= (total_ms / 1000.0) * 0.5
    score -= hints * 5
    score -= retries * 3
    score = round(max(0, score), 2)

    return {
        "total_time_s": round(total_ms / 1000, 3) if total_ms else None,
        "hints": hints,
        "retries": retries,
        "hesitation_s": round(hesitation_ms / 1000, 3),
        "performance_score": score,
    }


def compute_cognitive_metrics(session: dict) -> dict:
    """
    Compute metrics from cognitive sessions.
    Accuracy is computed by comparing user_answer to correct answer.
    """

    modules = session.get("modules", [])

    total_questions = 0
    scored_questions = 0
    correct_answers = 0
    total_time = 0.0

    for m in modules:
        for q in m.get("questions", []):
            total_questions += 1

            correct_answer = q.get("correct")
            user_answer = q.get("user_answer")

            # Only questions with a declared correct answer
            # participate in accuracy scoring.
            if correct_answer is not None:
                scored_questions += 1

                if (
                    user_answer is not None
                    and str(user_answer).strip()
                    == str(correct_answer).strip()
                ):
                    correct_answers += 1

            total_time += q.get("time_taken_seconds", 0) or 0

    if total_questions == 0:
        return {"note": "no questions"}

    accuracy_pct = None

    if scored_questions > 0:
        accuracy_pct = round(
            (correct_answers / scored_questions) * 100,
            2,
        )

    return {
        "accuracy_pct": accuracy_pct,
        "avg_time_s": round(
            total_time / total_questions,
            2,
        ),
        "question_count": total_questions,
        "scored_question_count": scored_questions,
    }

def aggregate_metrics(records=None):
    """
    Produce an aggregated summary.
    If your project already has export_all() returning session dicts,
    call this without arguments and handle None upstream.
    """
    if records is None:
        return {}

    summary = {
        "count": len(records),
        "behavioral": 0,
        "cognitive": 0,
    }

    for r in records:
        if isinstance(r, dict) and "events" in r:
            summary["behavioral"] += 1
        elif isinstance(r, dict) and "modules" in r:
            summary["cognitive"] += 1

    return summary

