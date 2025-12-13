"""
project/app/core/scoring.py

Pure scoring + signal extraction logic.
NO Flask imports.
NO request/response objects.

This module converts a task attempt into
structured, analyzable metrics.
"""
# project/app/core/scoring.py

from typing import Dict, Any
import time


def score_task_attempt(
    task: Dict[str, Any],
    submitted_answer: str | None,
    started_at_ms: int | None = None,
    submitted_at_ms: int | None = None,
) -> Dict[str, Any]:
    """
    Scores a single task attempt and returns standardized metrics.

    This function is intentionally domain-agnostic:
    - Works for cognitive, behavioral, HR, education, etc.
    - Does NOT store data (pure logic)
    """

    correct_answer = task.get("answer")
    is_correct = submitted_answer is not None and submitted_answer == correct_answer

    # Timing
    latency_ms = None
    if started_at_ms and submitted_at_ms:
        latency_ms = max(0, submitted_at_ms - started_at_ms)

    return {
        "task_id": task.get("task_id"),
        "category": task.get("category"),
        "difficulty": task.get("difficulty"),
        "submitted_answer": submitted_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "latency_ms": latency_ms,
        "scored_at_ms": int(time.time() * 1000),
    }


