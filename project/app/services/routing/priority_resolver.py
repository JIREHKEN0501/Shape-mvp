from typing import Dict, Any


def resolve_signal_priorities(
    arbitration_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply routing governance and conflict suppression.

    IMPORTANT:
    Priority resolution governs session-level adaptation only.
    """

    resolved = dict(arbitration_result)

    reasons = resolved.get("reasons", [])

    # ===================================
    # FATIGUE/STABILIZATION OVERRIDE
    # ===================================

    if resolved.get("stabilize"):

        # Suppress escalation
        if resolved.get("increase_difficulty"):

            resolved["increase_difficulty"] = False

            reasons.append(
                "Difficulty escalation suppressed by stabilization priority"
            )

    # ===================================
    # REDUCTION OVERRIDE
    # ===================================

    if resolved.get("reduce_difficulty"):

        if resolved.get("increase_difficulty"):

            resolved["increase_difficulty"] = False

            reasons.append(
                "Difficulty escalation suppressed by reduction priority"
            )

    # ===================================
    # FINAL CONFLICT CLEANUP
    # ===================================

    remaining_conflict = (
        resolved.get("increase_difficulty")
        and resolved.get("reduce_difficulty")
    )

    resolved["conflict_detected"] = bool(
        remaining_conflict
    )

    if not remaining_conflict:
        reasons.append(
            "Priority resolution completed successfully"
        )

    resolved["reasons"] = reasons

    return resolved
