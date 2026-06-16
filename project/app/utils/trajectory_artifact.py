# project/app/utils/trajectory_artifact.py


def build_trajectory_artifact(metrics: dict) -> dict:
    """
    Build a validation artifact from participant metrics.

    This artifact is intended for evaluator validation.
    It summarizes observable trajectory evidence without
    making psychological or diagnostic claims.
    """

    accuracy = metrics.get("accuracy", 0)

    avg_hesitation = metrics.get(
        "avg_hesitation",
        0,
    )

    attempts = metrics.get(
        "attempts",
        0,
    )

    difficulty_1 = metrics.get(
        "difficulty_1",
        0,
    )

    difficulty_2 = metrics.get(
        "difficulty_2",
        0,
    )

    difficulty_3 = metrics.get(
        "difficulty_3",
        0,
    )

    # ---------------------------------
    # Performance Stability
    # ---------------------------------

    if accuracy >= 95:
        performance_stability = "high"

    elif accuracy >= 80:
        performance_stability = "moderate"

    else:
        performance_stability = "low"

    # ---------------------------------
    # Challenge Retention
    # ---------------------------------

    high_difficulty_attempts = difficulty_3

    if (
        high_difficulty_attempts >= 10
        and accuracy >= 90
    ):
        challenge_retention = "strong"

    elif accuracy >= 75:
        challenge_retention = "moderate"

    else:
        challenge_retention = "weak"

    # ---------------------------------
    # Observed Friction
    # ---------------------------------

    if avg_hesitation >= 3:
        observed_friction = "high"

    elif avg_hesitation >= 1:
        observed_friction = "moderate"

    else:
        observed_friction = "low"

    # ---------------------------------
    # Trajectory Direction
    # ---------------------------------

    if accuracy >= 90:
        trajectory_direction = "positive"

    elif accuracy >= 70:
        trajectory_direction = "stable"

    else:
        trajectory_direction = "negative"

    total_difficulty = (
        difficulty_1
        + difficulty_2
        + difficulty_3
    )

    if total_difficulty == 0:
        difficulty_balance = "unknown"

    elif (
        difficulty_1 > 0
        and difficulty_2 > 0
        and difficulty_3 > 0
    ):
        difficulty_balance = "balanced"

    elif difficulty_3 > difficulty_1:
        difficulty_balance = (
            "higher_challenge_exposure"
        )

    else:
        difficulty_balance = (
            "lower_challenge_exposure"
        )
    
    #------------------------------------
    # Trajectory Severity
    # -----------------------------------
    if accuracy >= 90:
        trajectory_severity = (
            "strong_positive"
        )

    elif accuracy >= 75:
        trajectory_severity = (
            "positive"
        )

    elif accuracy >= 60:
        trajectory_severity = (
            "neutral"
        )

    elif accuracy >= 40:
        trajectory_severity = (
            "concerning"
        )

    else:
        trajectory_severity = (
            "critical"
        )

    #------------------------------
    # Evidence Strength
    # -----------------------------

    if attempts >= 40:
        evidence_strength = "high"

    elif attempts >= 20:
        evidence_strength = "moderate"

    else:
        evidence_strength = "low"

    return {
        "participant_id": metrics.get(
            "participant_id"
        ),
        "attempts": attempts,
        "accuracy": accuracy,
        "avg_hesitation": avg_hesitation,
        "difficulty_exposure": {
            "difficulty_1": difficulty_1,
            "difficulty_2": difficulty_2,
            "difficulty_3": difficulty_3,
        },
        "performance_stability": (
            performance_stability
        ),
        "challenge_retention": (
            challenge_retention
        ),
        "observed_friction": (
            observed_friction
        ),
        "trajectory_direction": (
            trajectory_direction
        ),
        "supporting_evidence": [
            f"Accuracy: {accuracy}%",
            (
                f"Average hesitation: "
                f"{avg_hesitation}"
            ),
            (
                f"Difficulty exposure: "
                f"D1={difficulty_1}, "
                f"D2={difficulty_2}, "
                f"D3={difficulty_3}"
            ),
        ],
        "difficulty_balance": (
            difficulty_balance
        ),

        "trajectory_severity": (
            trajectory_severity
        ),

        "evidence_strength": (
            evidence_strength
        ),
    }
