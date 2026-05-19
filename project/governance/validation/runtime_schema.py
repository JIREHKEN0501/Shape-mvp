from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GovernanceState:
    """
    Active governance runtime state.
    """

    active_modes: List[str] = field(default_factory=list)

    authority_level: float = 1.0

    escalation_level: int = 0


@dataclass
class EvidenceState:
    """
    Runtime evidence sufficiency state.

    Represents how much meaningful orchestration evidence
    currently exists for legitimacy-sensitive evaluation.
    """

    evidence_score: float = 0.0

    evidence_sufficient: bool = False


@dataclass
class LegitimacyState:
    """
    Runtime legitimacy and confidence state.
    """

    confidence: float = 0.0

    legitimacy_established: bool = False

    rehabilitation_active: bool = False


@dataclass
class GovernanceTrace:
    """
    Governance observability surface.
    """

    routing_status: str = "unknown"

    reasoning: List[str] = field(default_factory=list)

    routing_directives: Dict[str, Any] = field(
        default_factory=dict
    )

    transparency_note: str = ""


@dataclass
class RuntimeGovernanceContext:
    """
    Canonical runtime governance validation context.

    Shared across:
    - assertions
    - telemetry
    - simulations
    - invariant validation
    """

    governance_state: GovernanceState = field(
        default_factory=GovernanceState
    )

    evidence_state: EvidenceState = field(
        default_factory=EvidenceState
    )

    legitimacy_state: LegitimacyState = field(
        default_factory=LegitimacyState
    )

    governance_trace: GovernanceTrace = field(
        default_factory=GovernanceTrace
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
