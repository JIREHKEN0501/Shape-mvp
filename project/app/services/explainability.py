"""
Explainability helpers for HumanOS.

This module provides transparent, non-diagnostic explanations
about how summaries, insights, and confidence scores are derived.
"""

def generate_explainability(summary: dict) -> dict:
    total_attempts = summary.get("total_attempts", 0)

    signals_used = [
        "task accuracy",
        "response latency",
        "task difficulty",
        "category coverage",
    ]

    signals_excluded = [
        "personality traits",
        "intelligence",
        "mental health status",
        "emotional state",
        "future behavior prediction",
        "intent or motivation",
    ]

    data_limitations = []

    if total_attempts < 5:
        data_limitations.append(
            "Limited number of task attempts; interpretations may be unstable."
        )

    if not summary.get("by_category"):
        data_limitations.append(
            "No category diversity observed."
        )

    return {
        "signals_used": signals_used,
        "signals_excluded": signals_excluded,
        "data_limitations": data_limitations,
        "interpretation_scope": (
            "These explanations describe observed task performance patterns only. "
            "They do not infer abilities, traits, diagnoses, or future outcomes."
        ),
    }

