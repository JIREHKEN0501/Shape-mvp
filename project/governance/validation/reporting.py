
from dataclasses import dataclass, field
from typing import Dict, List

from .assertions import AssertionResult
from .violations import GovernanceViolation


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


def generate_validation_report(
    results: List[AssertionResult],
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

    for result in results:
        for violation in result.violations:

            violations.append(violation)

            severity = violation.severity.value

            severity_counts[severity] = (
                severity_counts.get(severity, 0) + 1
            )

    governance_status = "stable"

    if failed_assertions > 0:
        governance_status = "degraded"

    if severity_counts.get("critical", 0) > 0:
        governance_status = "critical"

    return GovernanceValidationReport(
        total_assertions=total_assertions,
        passed_assertions=passed_assertions,
        failed_assertions=failed_assertions,
        violations=violations,
        severity_counts=severity_counts,
        governance_status=governance_status,
    )
