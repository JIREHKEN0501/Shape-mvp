from typing import List, Dict, Tuple

from .signal_schema import RoutingSignal


def normalize_signals(
    signals: List[RoutingSignal]
) -> List[RoutingSignal]:
    """
    Normalize routing signals before arbitration.

    Responsibilities:
    - deduplicate repeated signals
    - merge redundant observations
    - stabilize routing influence

    IMPORTANT:
    Normalization applies to session-level routing observations only.
    """

    grouped: Dict[
        Tuple[str, str],
        List[RoutingSignal]
    ] = {}

    # -----------------------------------
    # Group similar signals
    # -----------------------------------

    for signal in signals:

        key = (
            signal.signal_type,
            str(signal.value)
        )

        grouped.setdefault(key, []).append(signal)

    normalized = []

    # -----------------------------------
    # Merge grouped signals
    # -----------------------------------

    for (_, _), group in grouped.items():

        base = group[0]

        occurrences = len(group)

        # Slight confidence reinforcement
        # for repeated corroboration
        boosted_confidence = min(
            base.confidence + (0.03 * (occurrences - 1)),
            1.0
        )

        base.confidence = round(
            boosted_confidence,
            2
        )

        # Attach normalization metadata
        if base.metadata is None:
            base.metadata = {}

        base.metadata["occurrences"] = occurrences
        base.metadata["normalized"] = True

        normalized.append(base)

    return normalized
