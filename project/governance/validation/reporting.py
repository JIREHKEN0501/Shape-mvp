from dataclasses import dataclass, field
from typing import Dict, List

from .assertions import AssertionResult
from .violations import GovernanceViolation
from .arbitration import (
    ArbitrationResult,
)

@dataclass
class GovernanceValidationReport:
    """
    Aggregated governance validation report.

    Summarizes runtime constitutional integrity evaluation.
    """

    total_assertions: int

    passed_assertions: int

    failed_assertions: int

    violations: List[GovernanceViolation] = field(
        default_factory=list
    )

    severity_counts: Dict[str, int] = field(
        default_factory=dict
    )

    governance_status: str = "unknown"

    arbitration_active: bool = False

    arbitration_summaries: List[str] = field(
        default_factory=list
    )

    arbitration_authority_ceiling: float = 0.5

    arbitration_unresolved_ambiguities: List[
        str
    ] = field(
        default_factory=list
    )

    topology_integrity: str = "unknown"

    def to_dict(self) -> Dict[str, object]:
        """
        Serialize governance validation report.
        """

        return {
            "total_assertions": self.total_assertions,
            "passed_assertions": self.passed_assertions,
            "failed_assertions": self.failed_assertions,
            "governance_status": self.governance_status,
            "arbitration_active":
                self.arbitration_active,

            "arbitration_summaries":
                self.arbitration_summaries,

            "arbitration_authority_ceiling":
                self.arbitration_authority_ceiling,

            "arbitration_unresolved_ambiguities":
                self.arbitration_unresolved_ambiguities,
            "topology_integrity": (
                self.topology_integrity
            ),
            "severity_counts": self.severity_counts,
            "violations": [
                violation.to_dict()
                for violation in self.violations
            ],
        }


def generate_validation_report(
    results: List[AssertionResult],

    arbitration_results: List[
        ArbitrationResult
    ] | None = None,

) -> GovernanceValidationReport:
    """
    Aggregate assertion evaluation results into a
    unified governance validation report.
    """

    total_assertions = len(results)

    passed_assertions = sum(
        1 for result in results if result.passed
    )

    failed_assertions = sum(
        1 for result in results if not result.passed
    )

    violations: List[GovernanceViolation] = []

    severity_counts: Dict[str, int] = {}

    arbitration_active = False

    arbitration_summaries: List[str] = []

    arbitration_authority_ceiling = 1.0

    arbitration_unresolved_ambiguities: List[
        str
    ] = []

    for result in results:
        for violation in result.violations:

            violations.append(violation)

            severity = violation.severity.value

            severity_counts[severity] = (
                severity_counts.get(severity, 0) + 1
            )

    governance_status = "stable"
    topology_integrity = "stable"

    if failed_assertions > 0:
        governance_status = "degraded"

    if severity_counts.get("critical", 0) > 0:
        governance_status = "critical"
    topology_violations_present = any(
        violation.invariant.invariant_id
        == "INV-009"
        for violation in violations
    )

    if topology_violations_present:
        topology_integrity = "violated"

    if arbitration_results:

        arbitration_active = True

        arbitration_authority_ceiling = min(
            result.authority_ceiling
            for result in arbitration_results
        )

        for result in arbitration_results:

            arbitration_summaries.append(
                (
                    "dominant="
                    f"{result.dominant_principle.value}"
                )
            )

            arbitration_unresolved_ambiguities.extend(
                result.unresolved_ambiguities
            )

    return GovernanceValidationReport(
        total_assertions=total_assertions,
        passed_assertions=passed_assertions,
        failed_assertions=failed_assertions,
        violations=violations,
        severity_counts=severity_counts,
        governance_status=governance_status,

        arbitration_active=(
            arbitration_active
        ),

        arbitration_summaries=(
            arbitration_summaries
        ),

        arbitration_authority_ceiling=(
            arbitration_authority_ceiling
        ),

        arbitration_unresolved_ambiguities=(
            arbitration_unresolved_ambiguities
        ),
        topology_integrity=(
            topology_integrity
        ),
    )
