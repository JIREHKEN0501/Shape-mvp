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

    top_categories = []

    if accuracies:
        top_score = max(
            accuracies.values()
        )

        top_categories = [
            cat
            for cat, score
            in accuracies.items()
            if score == top_score
        ]

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
            if (
                len(top_categories) == 1
                and category in top_categories
            ):
                reason = "Strongest performing category relative to overall session"

            elif (
                len(top_categories) > 1
                and category in top_categories
            ):
                reason = (
                    "Performance was comparable to other "
                    "top-performing categories within "
                    "this session"
                )
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

        # Behavioral signature (hesitation × accuracy)
        hesitation_rate = stats.get("hesitation_rate", 0)

        if accuracy is not None and attempts < 2:
            insights["patterns"].append({
                "category": category,
                "pattern": "Limited data — behavioral pattern not yet characterised. More attempts needed for reliable interpretation.",
            })
        elif accuracy is not None:
            high_hes = hesitation_rate >= 0.5
            high_acc = accuracy >= 0.7

            if high_hes and high_acc:
                pattern = "Deliberate and accurate — explores options before committing and arrives at correct responses, suggesting a careful reasoning style"
            elif high_hes and not high_acc:
                pattern = "High uncertainty — explores multiple options but struggles to identify correct responses, suggesting this area may be challenging"
            elif not high_hes and high_acc:
                pattern = "Accurate with minimal observable hesitation — maintains strong performance within this domain while showing little decision friction"
            else:
                pattern = "Low observable hesitation with reduced accuracy — responses are committed with little decision friction but correctness remains inconsistent within this domain"

            insights["patterns"].append({
                "category": category,
                "pattern": pattern,
            })

    insights["notes"].append(
        "Insights are observational and non-diagnostic. They describe patterns, not abilities or limits."
    )

    return insights

