# project/app/services/reports.py

"""
Reporting helpers that turn raw analytics into a teacher-friendly summary.

Builds on:
- project.app.services.analytics.generate_participant_summary
"""

from typing import Dict, Any, List

from project.app.services.analytics import generate_participant_summary


def _pick_strengths_and_gaps(by_category: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    From a by_category dict, pick categories that look like strengths / gaps.

    Heuristic:
      - strength: accuracy >= 0.75 and attempts >= 2
      - gap: accuracy <= 0.5 and attempts >= 2
    """
    strengths: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    for cat, info in by_category.items():
        acc = info.get("accuracy")
        attempts = info.get("attempts", 0)
        if acc is None or attempts < 2:
            continue

        entry = {
            "category": cat,
            "accuracy": acc,
            "attempts": attempts,
            "avg_response_time_s": info.get("avg_response_time_s"),
        }

        if acc >= 0.75:
            strengths.append(entry)
        elif acc <= 0.5:
            gaps.append(entry)

    strengths.sort(key=lambda e: (-e["accuracy"], -e["attempts"]))
    gaps.sort(key=lambda e: (e["accuracy"], -e["attempts"]))

    return {"strengths": strengths, "gaps": gaps}


def build_participant_report(participant_id: str) -> Dict[str, Any]:
    """
    Build a compact, teacher-friendly report for a participant.

    {
      "ok": True/False,
      "participant_id": "...",
      "summary": {...},
      "skills": {"strengths": [...], "gaps": [...]},
      "raw": {...full analytics summary...}
    }
    """
    summary = generate_participant_summary(participant_id)

    if not summary.get("has_data"):
        return {
            "ok": False,
            "participant_id": participant_id,
            "error": summary.get("message", "no_data"),
        }

    by_category = summary.get("by_category") or {}
    skills = _pick_strengths_and_gaps(by_category)

    report = {
        "ok": True,
        "participant_id": participant_id,
        "summary": {
            "total_attempts": summary.get("total_attempts"),
            "correct_attempts": summary.get("correct_attempts"),
            "wrong_attempts": summary.get("wrong_attempts"),
            "accuracy": summary.get("accuracy"),
            "sessions_count": summary.get("sessions_count"),
            "first_activity_ts": summary.get("first_activity_ts"),
            "last_activity_ts": summary.get("last_activity_ts"),
        },
        "skills": skills,
        "raw": summary,
    }

    return report

