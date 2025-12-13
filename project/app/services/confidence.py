"""
Confidence & uncertainty evaluation for HumanOS insights.
"""

def evaluate_confidence(summary: dict) -> dict:
    attempts = summary.get("total_attempts", 0)
    categories = summary.get("by_category", {})
    latency = summary.get("latency_ms", {})

    uncertainty_factors = []

    # ---- Basic sufficiency rules ----
    if attempts < 3:
        uncertainty_factors.append("Very limited number of task attempts.")

    if len(categories) < 2:
        uncertainty_factors.append("Performance observed in few task categories.")

    if latency and latency.get("sample_size", 0) < 3:
        uncertainty_factors.append("Reaction-time patterns based on limited samples.")

    # ---- Confidence scoring ----
    score = 1.0

    if attempts < 3:
        score -= 0.4
    elif attempts < 6:
        score -= 0.2

    if len(categories) < 2:
        score -= 0.2

    if uncertainty_factors:
        score -= 0.1 * len(uncertainty_factors)

    score = max(0.0, min(1.0, score))

    if score >= 0.75:
        level = "high"
    elif score >= 0.4:
        level = "medium"
    else:
        level = "low"

    return {
        "confidence_level": level,
        "confidence_score": round(score, 2),
        "data_sufficiency": score >= 0.4,
        "uncertainty_factors": uncertainty_factors,
        "note": (
            "Confidence reflects data volume and consistency, "
            "not user ability, intelligence, or potential."
        ),
    }

