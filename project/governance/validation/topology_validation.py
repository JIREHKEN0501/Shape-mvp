from typing import Optional

from .topology import (
    CANONICAL_GOVERNANCE_TOPOLOGY,
    GovernanceTransition,
)


def is_transition_allowed(
    source: str,
    target: str,
) -> bool:
    """
    Determine whether a governance transition
    is constitutionally allowed.
    """

    forbidden = (
        CANONICAL_GOVERNANCE_TOPOLOGY
        .forbidden_transitions
        .get(source, set())
    )

    if target in forbidden:
        return False

    allowed = (
        CANONICAL_GOVERNANCE_TOPOLOGY
        .allowed_transitions
        .get(source, set())
    )

    return target in allowed


def requires_reevaluation(
    source: str,
    target: str,
) -> bool:
    """
    Determine whether a governance transition
    requires reevaluation-sensitive validation.
    """

    for transition in (
        CANONICAL_GOVERNANCE_TOPOLOGY
        .reevaluation_gated_transitions
    ):

        if (
            transition.source == source
            and transition.target == target
        ):
            return (
                transition.reevaluation_required
            )

    return False


def get_transition_definition(
    source: str,
    target: str,
) -> Optional[GovernanceTransition]:
    """
    Retrieve canonical transition definition
    if one exists.
    """

    for transition in (
        CANONICAL_GOVERNANCE_TOPOLOGY
        .reevaluation_gated_transitions
    ):

        if (
            transition.source == source
            and transition.target == target
        ):
            return transition

    return None
