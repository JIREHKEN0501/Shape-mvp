# project/app/core/insights.py

from typing import Dict, Any
from collections import defaultdict
import statistics


def generate_insights(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate non-diagnostic, explainable insights from participant summary data.

    Input expected (from generate_participant_summary):
    - per_category stats
    - accuracy, latency, difficulty distributions
    """

    insights = {
        "strengths": [],
        "growth_areas": [],
        "patterns": [],
        "notes": [],
    }

    categories = summary.get("by_category", {})
    if not categories:
        insights["notes"].append("Not enough data to generate insights yet.")
        return insights

    for category, stats in categories.items():
        attempts = stats.get("attempts", 0)
        accuracy = stats.get("accuracy")
        avg_latency = stats.get("avg_latency_ms")
        avg_difficulty = stats.get("avg_difficulty")

        if attempts < 3:
            continue  # too little data to infer safely

        # Strength signal
        if accuracy is not None and accuracy >= 0.8:
            insights["strengths"].append({
                "category": category,
                "reason": "High accuracy relative to own performance history",
                "confidence": "medium",
            })

        # Growth signal
        if accuracy is not None and accuracy < 0.5:
            insights["growth_areas"].append({
                "category": category,
                "reason": "Lower accuracy suggests learning friction",
                "confidence": "low",
            })

        # Speed pattern
        if avg_latency is not None:
            if avg_latency < 2000:
                insights["patterns"].append({
                    "category": category,
                    "pattern": "Fast response speed",
                })
            elif avg_latency > 5000:
                insights["patterns"].append({
                    "category": category,
                    "pattern": "Deliberate / slower response style",
                })

    insights["notes"].append(
        "Insights are observational and non-diagnostic. They describe patterns, not abilities or limits."
    )

    return insights

