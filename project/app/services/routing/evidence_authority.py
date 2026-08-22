from typing import Any


ROUTING_AUTHORITY_POLICY_VERSION = "1.0"


ROUTING_AUTHORITY = {
    "fatigue_risk": "stabilize",
    "latency_trend": "reduce_difficulty",
    "accuracy_trend": "increase_difficulty",
}


def evaluate_routing_authority(
    signal_type: str,
    evidence_class: str | None,
) -> dict[str, Any]:
    """
    Determine whether a routing signal is authorized to influence
    a routing directive.

    Evidence classification and routing authority are deliberately
    separate concepts.

    A signal may be valid evidence without being authorized to
    produce a routing directive.
    """

    directive = ROUTING_AUTHORITY.get(signal_type)

    if directive is None:
        return {
            "policy_version": ROUTING_AUTHORITY_POLICY_VERSION,
            "signal_type": signal_type,
            "evidence_class": evidence_class,
            "routing_authorized": False,
            "authorized_directive": None,
            "reason": "No routing directive is authorized for this signal.",
        }

    return {
        "policy_version": ROUTING_AUTHORITY_POLICY_VERSION,
        "signal_type": signal_type,
        "evidence_class": evidence_class,
        "routing_authorized": True,
        "authorized_directive": directive,
        "reason": (
            "Signal type is explicitly authorized for the "
            "corresponding routing directive."
        ),
    }
