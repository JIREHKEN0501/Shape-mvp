# project/app/utils/trajectory_dynamics.py


def build_trajectory_dynamics(
    attempts: list,
) -> dict:
    """
    Analyze movement across a participant's
    session trajectory.

    Input:
        ordered task attempts

    Output:
        trajectory trends
    """

    if len(attempts) < 9:
        return {
            "accuracy_trend": "insufficient_data",
            "hesitation_trend": "insufficient_data",
            "difficulty_trend": "insufficient_data",
            "trajectory_state": "insufficient_data",
        }

    segment_size = len(attempts) // 3

    early = attempts[:segment_size]

    middle = attempts[
        segment_size:
        segment_size * 2
    ]

    late = attempts[
        segment_size * 2:
    ]

    early_accuracy = segment_accuracy(
        early
    )

    middle_accuracy = segment_accuracy(
        middle
    )

    late_accuracy = segment_accuracy(
        late
    )

    accuracy_range = (
        max(
            early_accuracy,
            middle_accuracy,
            late_accuracy,
        )
        -
        min(
            early_accuracy,
            middle_accuracy,
            late_accuracy,
        )
    )

    early_hesitation = segment_hesitation(
        early
    )

    middle_hesitation = segment_hesitation(
        middle
    )

    late_hesitation = segment_hesitation(
        late
    )

    if (
        late_accuracy
        > early_accuracy + 10
    ):
        accuracy_trend = "improving"

    elif (
        early_accuracy
        > late_accuracy + 10
    ):
        accuracy_trend = "declining"

    else:
        accuracy_trend = "stable"

    if (
        early_hesitation
        > late_hesitation + 1
    ):
        hesitation_trend = "decreasing"

    elif (
        late_hesitation
        > early_hesitation + 1
    ):
        hesitation_trend = "increasing"

    else:
        hesitation_trend = "stable"

    # ---------------------------------
    # Trajectory Shape
    # ---------------------------------

    if (
        early_accuracy > middle_accuracy
        and late_accuracy > middle_accuracy
    ):
        trajectory_shape = "recovery"

    elif (
        early_accuracy < middle_accuracy
        and middle_accuracy < late_accuracy
    ):
        trajectory_shape = "improvement"

    elif (
        early_accuracy > middle_accuracy
        and middle_accuracy > late_accuracy
    ):
        trajectory_shape = "decline"

    elif (
        early_accuracy < middle_accuracy
        and late_accuracy < middle_accuracy
    ):
        trajectory_shape = "peak_then_fall"

    else:
        trajectory_shape = "stable"

    # ---------------------------------
    # Trajectory State
    # ---------------------------------

    if trajectory_shape == "recovery":
        trajectory_state = "recovering"

    elif trajectory_shape == "improvement":
        trajectory_state = "improving"

    elif trajectory_shape == "decline":
        trajectory_state = "declining"

    elif (
        trajectory_shape == "stable"
        and accuracy_range >= 25
    ):
        trajectory_state = "volatile"

    else:
        trajectory_state = "stable"

    return {
        "early_accuracy": early_accuracy,
        "middle_accuracy": middle_accuracy,
        "late_accuracy": late_accuracy,

        "early_hesitation": early_hesitation,
        "middle_hesitation": middle_hesitation,
        "late_hesitation": late_hesitation,

        "accuracy_range": round(
             accuracy_range,
             2,
        ),

        "accuracy_trend": accuracy_trend,
        "hesitation_trend": hesitation_trend,
        "trajectory_state": (
            trajectory_state
        ),
        "trajectory_shape": (
            trajectory_shape
        ),
    }

def segment_accuracy(
    segment: list,
) -> float:

    if not segment:
        return 0

    correct = 0

    for attempt in segment:

        if attempt.get(
            "is_correct"
        ):
            correct += 1

    return round(
        (correct / len(segment))
        * 100,
        2,
    )

def segment_hesitation(
    segment: list,
) -> float:

    if not segment:
        return 0

    total = 0

    for attempt in segment:

        total += attempt.get(
            "hesitation",
            0,
        )

    return round(
        total / len(segment),
        2,
    )
