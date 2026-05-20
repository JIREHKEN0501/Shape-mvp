from dataclasses import dataclass
from enum import Enum
from typing import Dict


class InvariantSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass(frozen=True)
class GovernanceInvariant:
    """
    Canonical runtime representation of a governance invariant.

    Governance invariants represent constitutional orchestration protections
    derived from HumanOS governance ontology semantics.
    """

    invariant_id: str
    name: str
    severity: InvariantSeverity
    description: str
    rationale: str


INVARIANTS: Dict[str, GovernanceInvariant] = {
    "INV-001": GovernanceInvariant(
        invariant_id="INV-001",
        name="Restriction Precedes Restoration",
        severity=InvariantSeverity.CRITICAL,
        description=(
            "Governance restriction states must constrain unrestricted "
            "authority restoration until reevaluation-sensitive recovery "
            "conditions stabilize sufficiently."
        ),
        rationale=(
            "Prevents authority whiplash and premature legitimacy restoration."
        ),
    ),

    "INV-002": GovernanceInvariant(
        invariant_id="INV-002",
        name="Persistence Does Not Equal Legitimacy",
        severity=InvariantSeverity.CRITICAL,
        description=(
            "Temporal persistence alone must not establish orchestration legitimacy."
        ),
        rationale=(
            "Prevents false legitimacy accumulation from duration alone."
        ),
    ),

    "INV-003": GovernanceInvariant(
        invariant_id="INV-003",
        name="Operational Existence Does Not Equal Failure",
        severity=InvariantSeverity.MAJOR,
        description=(
            "Cold-start or sparse-evidence orchestration conditions must remain "
            "distinct from orchestration instability or failure."
        ),
        rationale=(
            "Prevents false instability signaling during insufficient evidence states."
        ),
    ),

    "INV-004": GovernanceInvariant(
        invariant_id="INV-004",
        name="Governance Visibility Required",
        severity=InvariantSeverity.CRITICAL,
        description=(
            "Governance restrictions, legitimacy gating, and escalation influences "
            "must remain observable through governance traces."
        ),
        rationale=(
            "Preserves explainability and governance auditability."
        ),
    ),

    "INV-005": GovernanceInvariant(
        invariant_id="INV-005",
        name="Governance Reversibility Preserved",
        severity=InvariantSeverity.MAJOR,
        description=(
            "Governance restriction states must remain theoretically reversible "
            "through reevaluation-sensitive recovery progression."
        ),
        rationale=(
            "Prevents pathological governance persistence and irreversible containment."
        ),
    ),

    "INV-006": GovernanceInvariant(
        invariant_id="INV-006",
        name="Escalation Must Remain Proportional",
        severity=InvariantSeverity.MAJOR,
        description=(
            "Escalation progression should remain severity-sensitive, "
            "evidence-aware, and reevaluation-conscious."
        ),
        rationale=(
            "Prevents disproportionate containment behavior."
        ),
    ),

    "INV-007": GovernanceInvariant(
        invariant_id="INV-007",
        name="Reevaluation Must Remain Meaningful",
        severity=InvariantSeverity.MAJOR,
        description=(
            "Governance reevaluation should contribute meaningful legitimacy "
            "reassessment rather than passive governance cycling."
        ),
        rationale=(
            "Prevents reevaluation stagnation and deadlock cycling."
        ),
    ),

    "INV-008": GovernanceInvariant(
        invariant_id="INV-008",
        name="Confidence Rehabilitation Must Remain Constrained",
        severity=InvariantSeverity.MAJOR,
        description=(
            "Confidence rehabilitation should remain gradual, "
            "evidence-sensitive, and governance-aware."
        ),
        rationale=(
            "Prevents legitimacy inflation and unstable authority rebounds."
        ),
    ),

    "INV-009": GovernanceInvariant(
        invariant_id="INV-009",
        name="Governance Transition Legality",
        severity=InvariantSeverity.CRITICAL,
        description=(
            "Governance transitions must follow "
            "canonical topology legality."
        ),
        rationale=(
            "Prevents illegal authority restoration "
            "and invalid governance progression."
        ),
    ),
}


def get_invariant(invariant_id: str) -> GovernanceInvariant | None:
    """
    Retrieve a governance invariant by invariant identifier.
    """
    return INVARIANTS.get(invariant_id)


def list_invariants() -> Dict[str, GovernanceInvariant]:
    """
    Return all registered governance invariants.
    """
    return INVARIANTS
