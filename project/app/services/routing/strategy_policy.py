from typing import Any, Dict, List

from .signal_schema import RoutingSignal


STRATEGY_POLICY_VERSION = "1.0"


def evaluate_strategy_policy(
    signals: List[RoutingSignal],
) -> Dict[str, Any]:
    """
    Evaluate strategy evidence for routing eligibility.

    Strategy decisions are observations derived from a governed
    task definition. They do not acquire routing authority merely
    because they exist.

    Current policy:
        - Preserve recognized strategy observations.
        - Do not convert strategy decisions into routing directives.
        - Make the absence of routing authority explicit.

    Future policy changes must explicitly authorize a decision_code
    before it can influence orchestration.
    """

    strategy_observations = []

    for signal in signals:
        if signal.signal_type != "strategy_decision":
            continue

        metadata = signal.metadata or {}

        strategy_observations.append({
            "question_id": metadata.get("question_id"),
            "selected_option": metadata.get("selected_option"),
            "decision_code": signal.value,
            "evidence_class": metadata.get(
                "evidence_class",
                "observation",
            ),
        })

    return {
        "policy_version": STRATEGY_POLICY_VERSION,
        "strategy_observations": strategy_observations,
        "routing_authorized": False,
        "authorized_directives": [],
        "reason": (
            "Strategy decisions are evidence-only unless an "
            "explicit routing policy authorizes a directive."
        ),
    }
