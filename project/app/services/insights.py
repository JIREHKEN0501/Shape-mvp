def generate_insights(summary: dict) -> dict:
    insights = {
        "accuracy": [],
        "speed": [],
        "coverage": [],
        "stability": [],
        "notes": [],
    }

    total = summary.get("total_attempts", 0)
    accuracy = summary.get("accuracy")

    # --- Accuracy insight ---
    if total > 0 and accuracy is not None:
        if accuracy >= 0.8:
            insights["accuracy"].append(
                "Strong overall accuracy, suggesting reliable understanding."
            )
        elif accuracy >= 0.5:
            insights["accuracy"].append(
                "Accuracy is developing; performance improves with continued practice."
            )
        else:
            insights["accuracy"].append(
                "Accuracy is currently low; additional support or simpler tasks may help."
            )

    # --- Category balance ---
    by_category = summary.get("by_category", {})
    if by_category:
        dominant = max(by_category.items(), key=lambda x: x[1]["attempts"])[0]
        insights["coverage"].append(
            f"Most activity occurred in '{dominant.replace('_', ' ')}' tasks."
        )

    # --- Speed insight ---
    attempts = []
    for task in summary.get("by_task", {}).values():
        attempts.extend(task.get("attempts", []))

    latencies = [a.get("latency_ms") for a in attempts if isinstance(a.get("latency_ms"), (int, float))]

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        if avg_latency < 2000:
            insights["speed"].append(
                "Responses are generally fast, indicating quick decision-making."
            )
        elif avg_latency < 5000:
            insights["speed"].append(
                "Response times suggest a thoughtful and deliberate pace."
            )
        else:
            insights["speed"].append(
                "Longer response times may indicate careful reasoning or increased difficulty."
            )

    # --- Stability insight ---
    if total >= 5:
        insights["stability"].append(
            "Performance shows reasonable stability across attempts."
        )

    if not any(insights.values()):
        insights["notes"].append("Not enough data to generate detailed insights yet.")

    return insights

