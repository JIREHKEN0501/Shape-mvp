from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class GovernanceTransition:
    """
    Canonical governance transition definition.
    """

    source: str

    target: str

    allowed: bool = True

    reevaluation_required: bool = False

    notes: str = ""


@dataclass
class GovernanceTopology:
    """
    Canonical governance transition topology.
    """

    allowed_transitions: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    forbidden_transitions: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    reevaluation_gated_transitions: List[
        GovernanceTransition
    ] = field(default_factory=list)


CANONICAL_GOVERNANCE_TOPOLOGY = GovernanceTopology(

    allowed_transitions={

        "unrestricted": {
            "low_authority",
            "stabilization",
            "suppression",
        },

        "low_authority": {
            "stabilization",
            "unrestricted",
        },

        "stabilization": {
            "rehabilitation",
        },

        "rehabilitation": {
            "low_authority",
        },

        "suppression": {
            "stabilization",
        },

        "escalation_review": {
            "stabilization",
            "suppression",
        },
    },

    forbidden_transitions={

        "suppression": {
            "unrestricted",
            "rehabilitation",
        },

        "stabilization": {
            "unrestricted",
        },

        "escalation_review": {
            "unrestricted",
        },

        "rehabilitation": {
            "unrestricted",
        },

        "unrestricted": {
            "rehabilitation",
        },
    },

    reevaluation_gated_transitions=[

        GovernanceTransition(
            source="stabilization",
            target="rehabilitation",
            reevaluation_required=True,
        ),

        GovernanceTransition(
            source="rehabilitation",
            target="low_authority",
            reevaluation_required=True,
        ),

        GovernanceTransition(
            source="low_authority",
            target="unrestricted",
            reevaluation_required=True,
        ),

        GovernanceTransition(
            source="escalation_review",
            target="stabilization",
            reevaluation_required=True,
        ),
    ],
)
