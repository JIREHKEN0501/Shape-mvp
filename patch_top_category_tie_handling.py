from pathlib import Path

path = Path(
    "project/app/core/insights.py"
)

text = path.read_text()

old = """accuracies = {
        cat: stats.get("accuracy", 0)
        for cat, stats in categories.items()
    }
    top_category = max(accuracies, key=accuracies.get) if accuracies else None"""

new = """accuracies = {
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
        ]"""

text = text.replace(old, new)

old = """if category == top_category:
                reason = "Strongest performing category relative to overall session\""""

new = """if (
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
                )"""

text = text.replace(old, new)

path.write_text(text)

print("Patch applied.")
