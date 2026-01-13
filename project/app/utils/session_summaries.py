# project/app/utils/session_summaries.py

import statistics
from project.app.utils.helpers import now_iso


def build_cognitive_session_summary(session: dict) -> dict:
    modules = session.get("modules", [])
    questions = []

    for m in modules:
        questions.extend(m.get("questions", []))

    total = len(questions)
    if total == 0:
        return {
            "total_questions": 0,
            "accuracy_ratio": None,
            "avg_time_per_question": None,
            "median_time_per_question": None,
            "time_variance": None,
            "speed_accuracy_profile": "insufficient_data",
        }

    correct_count = 0
    for q in questions:
        correct = q.get("correct")
        user_answer = q.get("user_answer")

        if (
            correct is not None
            and user_answer is not None
            and str(correct).strip() == str(user_answer).strip()
        ):
            correct_count += 1

    times = [
        q["time_taken_seconds"]
        for q in questions
        if isinstance(q.get("time_taken_seconds"), (int, float))
    ]

    avg_time = round(statistics.mean(times), 3) if times else None
    median_time = round(statistics.median(times), 3) if times else None
    variance = round(statistics.pvariance(times), 3) if len(times) > 1 else 0.0

    accuracy_ratio = round(correct_count / total, 3)

    if avg_time is None:
        profile = "insufficient_data"
    elif accuracy_ratio >= 0.75 and avg_time <= 6:
        profile = "fast_accurate"
    elif accuracy_ratio >= 0.75:
        profile = "slow_accurate"
    elif avg_time <= 6:
        profile = "fast_inaccurate"
    else:
        profile = "slow_inaccurate"

    return {
        "total_questions": total,
        "accuracy_ratio": accuracy_ratio,
        "avg_time_per_question": avg_time,
        "median_time_per_question": median_time,
        "time_variance": variance,
        "speed_accuracy_profile": profile,
    }

