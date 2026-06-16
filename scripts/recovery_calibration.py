import json
from collections import defaultdict


LOG_FILE = "logs/data_log.jsonl"


participants = defaultdict(list)


with open(LOG_FILE, "r") as f:

    for line in f:

        try:
            event = json.loads(line)

        except Exception:
            continue

        if event.get("event_type") != "task_attempt":
            continue

        pid = event.get("participant_id")

        metrics = event.get(
            "metrics",
            {},
        )

        participants[pid].append(
            {
                "is_correct": metrics.get(
                    "is_correct",
                    False,
                )
            }
        )


def segment_accuracy(
    segment,
):

    if not segment:
        return 0

    correct = sum(
        1
        for x in segment
        if x["is_correct"]
    )

    return round(
        (correct / len(segment))
        * 100,
        2,
    )


print(
    "\n=== RECOVERY CALIBRATION ===\n"
)


for pid, attempts in participants.items():

    if len(attempts) < 20:
        continue

    segment_size = (
        len(attempts)
        // 3
    )

    early = attempts[
        :segment_size
    ]

    middle = attempts[
        segment_size:
        segment_size * 2
    ]

    late = attempts[
        segment_size * 2:
    ]

    early_acc = (
        segment_accuracy(
            early
        )
    )

    middle_acc = (
        segment_accuracy(
            middle
        )
    )

    late_acc = (
        segment_accuracy(
            late
        )
    )

    drop = round(
        middle_acc
        - early_acc,
        2,
    )

    rebound = round(
        late_acc
        - middle_acc,
        2,
    )

    recovery_candidate = (
        rebound >= 15
    )

    print(
        f"{pid} | "
        f"E={early_acc} "
        f"M={middle_acc} "
        f"L={late_acc} | "
        f"Drop={drop} "
        f"Rebound={rebound} | "
        f"Recovery={recovery_candidate}"
    )
