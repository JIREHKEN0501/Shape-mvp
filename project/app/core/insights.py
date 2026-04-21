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

    
    # --- Global context (cross-category) ---
    latencies = [
        stats.get("avg_response_time_s")
        for stats in categories.values()
        if stats.get("avg_response_time_s") is not None
    ]
    overall_avg_latency = sum(latencies) / len(latencies) if latencies else None
    accuracies = {
        cat: stats.get("accuracy", 0)
        for cat, stats in categories.items()
    }
    top_category = max(accuracies, key=accuracies.get) if accuracies else None

    for category, stats in categories.items():
        attempts = stats.get("attempts", 0)
        accuracy = stats.get("accuracy")
        avg_latency = stats.get("avg_latency_ms") or (stats.get("avg_response_time_s") * 1000 if stats.get("avg_response_time_s") else None)
        avg_difficulty = stats.get("avg_difficulty")

        if attempts < 1:
            continue  # skip only if zero attempts

        # Strength signal
        if accuracy is not None and accuracy >= 0.75:
            if accuracy >= 0.9 and attempts >= 3:
                confidence = "high"
                reason = "Consistently high accuracy across multiple attempts indicates strong mastery"
            elif accuracy >= 0.8:
                confidence = "medium"
                reason = "Above-average accuracy suggests growing competence in this domain"
            else:
                confidence = "low"
                reason = "Moderate accuracy suggests developing but inconsistent performance"
            if category == top_category:
                reason = "Strongest performing category relative to overall session"
            insights["strengths"].append({
                "category": category,
                "reason": reason,
                "confidence": confidence,
            })

        # Growth signal
        if accuracy is not None and accuracy < 0.5:
            if accuracy == 0.0 and attempts >= 2:
                confidence = "high"
                reason = f"No correct responses across {attempts} attempts — consistent difficulty in this area"
            elif accuracy < 0.3:
                confidence = "medium"
                reason = "Very low accuracy suggests significant learning friction or unfamiliarity"
            else:
                confidence = "low"
                reason = "Below-average accuracy indicates an area worth focused attention"
            insights["growth_areas"].append({
                "category": category,
                "reason": reason,
                "confidence": confidence,
            })

        # Behavioral pattern (contextual)
        avg_seconds = stats.get("avg_response_time_s")
        if avg_seconds is not None and overall_avg_latency is not None:
            if avg_seconds > overall_avg_latency * 1.2:
                pattern = f"Average response time of {avg_seconds:.1f}s is slower relative to other categories, suggesting higher cognitive load"
            elif avg_seconds < overall_avg_latency * 0.8:
                pattern = f"Average response time of {avg_seconds:.1f}s is faster relative to other categories, suggesting stronger familiarity or confidence"
            else:
                pattern = f"Response time of {avg_seconds:.1f}s is consistent with overall session behavior"
            insights["patterns"].append({
                "category": category,
                "pattern": pattern,
            })

    insights["notes"].append(
        "Insights are observational and non-diagnostic. They describe patterns, not abilities or limits."
    )

    return insights

