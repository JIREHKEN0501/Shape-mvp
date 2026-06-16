import json

from collections import defaultdict

LOG_FILE = "logs/data_log.jsonl"

participants = defaultdict(
    lambda: {
        "attempts": 0,
        "correct": 0,
        "hesitation_sum": 0,
        "difficulty_1": 0,
        "difficulty_2": 0,
        "difficulty_3": 0,
    }
)

with open(LOG_FILE, "r") as f:
    for line in f:
        try:
            event = json.loads(line)
        except Exception:
            continue

        if event.get("event_type") != "task_attempt":
            continue

        pid = event.get("participant_id")
        metrics = event.get("metrics", {})

        participants[pid]["attempts"] += 1

        if metrics.get("is_correct"):
            participants[pid]["correct"] += 1

        participants[pid]["hesitation_sum"] += metrics.get(
            "hesitation",
            0,
        )

        difficulty = metrics.get("difficulty")

        if difficulty == 1:
            participants[pid]["difficulty_1"] += 1
        elif difficulty == 2:
            participants[pid]["difficulty_2"] += 1
        elif difficulty == 3:
            participants[pid]["difficulty_3"] += 1

results = []

zero_hesitation_count = 0
nonzero_hesitation_count = 0

highest_hesitation = None
lowest_nonzero_hesitation = None

zero_hesitation_participants = []

for pid, stats in participants.items():

    attempts = stats["attempts"]

    if attempts == 0:
        continue

    accuracy = (
        stats["correct"]
        / attempts
        * 100
    )

    avg_hesitation = (
        stats["hesitation_sum"]
        / attempts
    )

    if avg_hesitation == 0:
        zero_hesitation_count += 1
        zero_hesitation_participants.append(pid)
    else:
        nonzero_hesitation_count += 1

        if (
            lowest_nonzero_hesitation is None
            or avg_hesitation < lowest_nonzero_hesitation
        ):
            lowest_nonzero_hesitation = avg_hesitation

    if (
        highest_hesitation is None
        or avg_hesitation > highest_hesitation
    ):
        highest_hesitation = avg_hesitation

    results.append(
        {
            "participant": pid,
            "attempts": attempts,
            "accuracy": round(
                accuracy,
                2,
            ),
            "avg_hesitation": round(
                avg_hesitation,
                2,
            ),
            "difficulty_1": stats["difficulty_1"],
            "difficulty_2": stats["difficulty_2"],
            "difficulty_3": stats["difficulty_3"],
        }
    )

results.sort(
    key=lambda x: x["accuracy"],
    reverse=True,
)

print("\n=== TOP 20 BY ACCURACY ===\n")

for row in results[:20]:
    print(
        f"{row['participant']} | "
        f"Acc={row['accuracy']}% | "
        f"Hes={row['avg_hesitation']} | "
        f"Attempts={row['attempts']} | "
        f"D1={row['difficulty_1']} "
        f"D2={row['difficulty_2']} "
        f"D3={row['difficulty_3']}"
    )

print(
    f"\nParticipants analyzed: "
    f"{len(results)}"
)

qualified = [
    r for r in results
    if r["attempts"] >= 20
]

qualified_zero_hesitation = [
    r for r in qualified
    if r["avg_hesitation"] == 0
]

print("\n=== QUALIFIED PARTICIPANTS (20+ ATTEMPTS) ===\n")

for row in qualified:
    print(
        f"{row['participant']} | "
        f"Acc={row['accuracy']}% | "
        f"Hes={row['avg_hesitation']} | "
        f"Attempts={row['attempts']}"
    )

print(
    f"\nQualified participants: "
    f"{len(qualified)}"
)

print(
    f"Acc={row['accuracy']}% | "
    f"Hes={row['avg_hesitation']} | "
    f"Attempts={row['attempts']} | "
    f"D1={row['difficulty_1']} "
    f"D2={row['difficulty_2']} "
    f"D3={row['difficulty_3']}"
)

print("\n=== SIGNAL QUALITY AUDIT ===\n")

print(
    f"Participants with zero hesitation: "
    f"{zero_hesitation_count}"
)

print(
    f"Participants with non-zero hesitation: "
    f"{nonzero_hesitation_count}"
)

print(
    f"Highest average hesitation: "
    f"{round(highest_hesitation, 2)}"
)

if lowest_nonzero_hesitation is not None:
    print(
        f"Lowest non-zero hesitation: "
        f"{round(lowest_nonzero_hesitation, 2)}"
    )

print(
    f"\nQualified participants with "
    f"zero hesitation: "
    f"{len(qualified_zero_hesitation)}"
)

for row in qualified_zero_hesitation:
    print(
        f"{row['participant']} | "
        f"Acc={row['accuracy']}% | "
        f"Attempts={row['attempts']}"
    )
