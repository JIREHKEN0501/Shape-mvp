from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .invariants import GovernanceInvariant, get_invariant
from .telemetry import telemetry_buffer

from .runtime_normalization import (
    normalize_runtime_context,
)
from .violations import (
     GovernanceViolation,
     ViolationStatus,
)
from .constants import (
    FULL_AUTHORITY_LEVEL,
    HIGH_CONFIDENCE_THRESHOLD,
    SUFFICIENT_EVIDENCE_SCORE,
    HIGH_AUTHORITY_THRESHOLD,
    MAX_REEVALUATION_INTERVAL_SECONDS,
)
from .runtime_schema import RuntimeGovernanceContext

@dataclass
class AssertionResult:
    """
    Result produced by runtime governance assertion evaluation.
    """

    invariant: GovernanceInvariant
    passed: bool

    violations: List[GovernanceViolation] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


AssertionEvaluator = Callable[[Dict[str, Any]], AssertionResult]


ASSERTION_REGISTRY: Dict[str, AssertionEvaluator] = {}


def register_assertion(
    invariant_id: str,
    evaluator: AssertionEvaluator,
) -> None:
    """
    Register runtime assertion evaluator for a governance invariant.
    """

    ASSERTION_REGISTRY[invariant_id] = evaluator


def get_assertion(
    invariant_id: str,
) -> AssertionEvaluator | None:
    """
    Retrieve assertion evaluator by invariant identifier.
    """

    return ASSERTION_REGISTRY.get(invariant_id)


def evaluate_assertion(
    invariant_id: str,
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Evaluate governance assertion against runtime orchestration context.
    """

    invariant = get_invariant(invariant_id)

    if invariant is None:
        raise ValueError(
            f"Unknown governance invariant: {invariant_id}"
        )

    evaluator = get_assertion(invariant_id)

    if evaluator is None:
        return AssertionResult(
            invariant=invariant,
            passed=True,
            metadata={
                "note": (
                    "No assertion evaluator registered "
                    "for invariant."
                )
            },
        )

    return evaluator(runtime_context)


def evaluate_all_assertions(
    runtime_context: Dict[str, Any],
) -> List[AssertionResult]:
    """
    Evaluate all registered governance assertions.
    """

    results: List[AssertionResult] = []

    for invariant_id in ASSERTION_REGISTRY:
        result = evaluate_assertion(
            invariant_id,
            runtime_context,
        )

        results.append(result)

    return results


def evaluate_governance_visibility(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate governance visibility integrity.

    Ensures governance restrictions and escalation conditions
    remain observable through runtime governance traces.
    """

    invariant = get_invariant("INV-004")

    if invariant is None:
        raise ValueError("INV-004 invariant not registered.")

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):

        governance_trace = (
            runtime_context.governance_trace
        )

        active_modes = (
            runtime_context
            .governance_state
            .active_modes
        )

        governance_trace = {
            "routing_status": (
                governance_trace.routing_status
            ),
            "reasoning": (
                governance_trace.reasoning
            ),
            "routing_directives": (
                governance_trace.routing_directives
            ),
            "transparency_note": (
                governance_trace.transparency_note
            ),
        }

    else:

        governance_trace = runtime_context.get(
            "governance_trace"
        )

        active_modes = runtime_context.get(
            "governance_state",
            {}
        ).get(
            "active_modes",
            []
        )

    trace_has_visibility = bool(
        governance_trace
    ) and any(
        key in governance_trace
        for key in [
            "routing_status",
            "reasoning",
            "routing_directives",
            "transparency_note",
        ]
    )

    if not active_modes:
        trace_has_visibility = bool(governance_trace)

    if trace_has_visibility:
        telemetry_buffer.emit(
            event_type="governance_visibility_verified",
            payload={
                "invariant_id": invariant.invariant_id,
                "trace_present": True,
                "trace_visibility_verified": True,
                "active_modes_present": bool(active_modes),
            },
        )

        return AssertionResult(
            invariant=invariant,
            passed=True,
        )

    violation = GovernanceViolation(
        invariant=invariant,
        message=(
            "Governance trace missing or semantically incomplete "
            "during runtime orchestration."
        ),
        status=ViolationStatus.DETECTED,
        recommendation=(
            "Ensure governance restrictions, routing behavior, "
            "and escalation influences remain observable."
        ),
        metadata={
            "trace_present": bool(governance_trace),
            "trace_visibility_verified": False,
            "active_modes_present": bool(active_modes),
        },
    )
    return AssertionResult(
        invariant=invariant,
        passed=False,
        violations=[violation],
    )


register_assertion(
    invariant_id="INV-004",
    evaluator=evaluate_governance_visibility,
)

def evaluate_restriction_precedence(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate restriction precedence integrity.

    Ensures restrictive governance states constrain
    unrestricted authority restoration behavior.
    """

    invariant = get_invariant("INV-001")

    if invariant is None:
        raise ValueError("INV-001 invariant not registered.")

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):

        governance_state = (
            runtime_context.governance_state
        )

        active_modes = (
            governance_state.active_modes
        )

        authority_level = (
            governance_state.authority_level
        )

    else:

        governance_state = runtime_context.get(
            "governance_state",
            {}
        )

        active_modes = governance_state.get(
            "active_modes",
            []
        )

        authority_level = governance_state.get(
            "authority_level",
            1.0,
        )

    restrictive_modes = {
        "suppression",
        "stabilization",
        "escalation_review",
    }

    restrictive_active = any(
        mode in restrictive_modes
        for mode in active_modes
    )

    unrestricted_restoration = (
        authority_level >= FULL_AUTHORITY_LEVEL
    )
    if restrictive_active and unrestricted_restoration:
        violation = GovernanceViolation(
            invariant=invariant,
            message=(
                "Restrictive governance modes active during "
                "unrestricted authority restoration."
            ),
            status=ViolationStatus.DETECTED,
            recommendation=(
                "Ensure containment states constrain unrestricted "
                "authority rehabilitation."
            ),
            metadata={
                "active_modes": active_modes,
                "authority_level": authority_level,
            },
        )

        telemetry_buffer.emit(
            event_type="restriction_precedence_violation",
            payload=violation.to_dict(),
        )

        return AssertionResult(
            invariant=invariant,
            passed=False,
            violations=[violation],
        )

    telemetry_buffer.emit(
        event_type="restriction_precedence_verified",
        payload={
            "invariant_id": invariant.invariant_id,
            "active_modes": active_modes,
            "authority_level": authority_level,
        },
    )

    return AssertionResult(
        invariant=invariant,
        passed=True,
    )


register_assertion(
    invariant_id="INV-001",
    evaluator=evaluate_restriction_precedence,
)


def evaluate_persistence_legitimacy(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate persistence-sensitive legitimacy semantics.

    Ensures confidence and legitimacy progression remain
    evidence-sensitive rather than duration-inflated.
    """

    invariant = get_invariant("INV-002")

    if invariant is None:
        raise ValueError("INV-002 invariant not registered.")

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):

        legitimacy_state = (
            runtime_context.legitimacy_state
        )

        evidence_state = (
            runtime_context.evidence_state
        )

        confidence = (
            legitimacy_state.confidence
        )

        evidence_score = (
            evidence_state.evidence_score
        )

    else:

        legitimacy_state = runtime_context.get(
            "legitimacy_state",
            {}
        )

        evidence_state = runtime_context.get(
            "evidence_state",
            {}
        )

        confidence = legitimacy_state.get(
            "confidence",
            0.0,
        )

        evidence_score = evidence_state.get(
            "evidence_score",
            0.0,
        )

    evidence_sufficient = (
        evidence_score >= SUFFICIENT_EVIDENCE_SCORE
    )

    high_confidence = (
        confidence >= HIGH_CONFIDENCE_THRESHOLD
    )

    if high_confidence and not evidence_sufficient:
        violation = GovernanceViolation(
            invariant=invariant,
            message=(
                "High confidence established without "
                "sufficient supporting evidence."
            ),
            status=ViolationStatus.DETECTED,
            recommendation=(
                "Ensure legitimacy progression remains "
                "evidence-sensitive."
            ),
            metadata={
                "confidence": confidence,
                "evidence_score": evidence_score,
                "evidence_sufficient": evidence_sufficient,
            },
        )

        telemetry_buffer.emit(
            event_type="persistence_legitimacy_violation",
            payload=violation.to_dict(),
        )

        return AssertionResult(
            invariant=invariant,
            passed=False,
            violations=[violation],
        )

    telemetry_buffer.emit(
        event_type="persistence_legitimacy_verified",
        payload={
            "invariant_id": invariant.invariant_id,
            "confidence": confidence,
            "evidence_score": evidence_score,
            "evidence_sufficient": evidence_sufficient,
        },
    )

    return AssertionResult(
        invariant=invariant,
        passed=True,
    )


register_assertion(
    invariant_id="INV-002",
    evaluator=evaluate_persistence_legitimacy,
)


def evaluate_temporal_reevaluation_integrity(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate temporal reevaluation integrity.

    Ensures governance states remain periodically
    reevaluation-sensitive over time.
    """

    invariant = get_invariant("INV-007")

    if invariant is None:
        raise ValueError("INV-007 invariant not registered.")

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):

        temporal_state = (
            runtime_context.temporal_state
        )

        reevaluation_required = (
            temporal_state.reevaluation_required
        )

        last_evaluation_at = (
            temporal_state.last_evaluation_at
        )

    else:

        temporal_state = runtime_context.get(
            "temporal_state",
            {}
        )

        reevaluation_required = temporal_state.get(
            "reevaluation_required",
            False,
        )

        last_evaluation_at = temporal_state.get(
            "last_evaluation_at",
            "",
        )

    reevaluation_stale = False

    if reevaluation_required and not last_evaluation_at:

        reevaluation_stale = True

    if reevaluation_stale:

        violation = GovernanceViolation(
            invariant=invariant,
            message=(
                "Governance reevaluation overdue "
                "during active governance persistence."
            ),
            status=ViolationStatus.DETECTED,
            recommendation=(
                "Ensure governance states remain "
                "periodically reevaluated."
            ),
            metadata={
                "reevaluation_required": (
                    reevaluation_required
                ),
                "last_evaluation_at": (
                    last_evaluation_at
                ),
            },
        )

        telemetry_buffer.emit(
            event_type=(
                "temporal_reevaluation_violation"
            ),
            payload=violation.to_dict(),
        )

        return AssertionResult(
            invariant=invariant,
            passed=False,
            violations=[violation],
        )

    telemetry_buffer.emit(
        event_type=(
            "temporal_reevaluation_verified"
        ),
        payload={
            "invariant_id": invariant.invariant_id,
            "reevaluation_required": (
                reevaluation_required
            ),
            "last_evaluation_at": (
                last_evaluation_at
            ),
        },
    )

    return AssertionResult(
        invariant=invariant,
        passed=True,
    )


register_assertion(
    invariant_id="INV-007",
    evaluator=(
        evaluate_temporal_reevaluation_integrity
    ),
)


def evaluate_constrained_rehabilitation(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate rehabilitation pacing integrity.

    Ensures authority rehabilitation remains gradual and
    governance-aware during recovery progression.
    """

    invariant = get_invariant("INV-008")

    if invariant is None:
        raise ValueError("INV-008 invariant not registered.")

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):

        legitimacy_state = (
            runtime_context.legitimacy_state
        )

        governance_state = (
            runtime_context.governance_state
        )

        rehabilitation_active = (
            legitimacy_state.rehabilitation_active
        )

        authority_level = (
            governance_state.authority_level
        )

    else:

        legitimacy_state = runtime_context.get(
            "legitimacy_state",
            {}
        )

        governance_state = runtime_context.get(
            "governance_state",
            {}
        )

        rehabilitation_active = legitimacy_state.get(
            "rehabilitation_active",
            False,
        )

        authority_level = governance_state.get(
            "authority_level",
            0.0,
        )

    aggressive_rehabilitation = (
        rehabilitation_active
        and authority_level >= HIGH_AUTHORITY_THRESHOLD
    )

    if aggressive_rehabilitation:
        violation = GovernanceViolation(
            invariant=invariant,
            message=(
                "Authority rehabilitation progressing too aggressively "
                "during active recovery."
            ),
            status=ViolationStatus.DETECTED,
            recommendation=(
                "Ensure rehabilitation progression remains gradual "
                "and reevaluation-sensitive."
            ),
            metadata={
                "rehabilitation_active": rehabilitation_active,
                "authority_level": authority_level,
            },
        )

        telemetry_buffer.emit(
            event_type="rehabilitation_constraint_violation",
            payload=violation.to_dict(),
        )

        return AssertionResult(
            invariant=invariant,
            passed=False,
            violations=[violation],
        )

    telemetry_buffer.emit(
        event_type="rehabilitation_constraint_verified",
        payload={
            "invariant_id": invariant.invariant_id,
            "rehabilitation_active": rehabilitation_active,
            "authority_level": authority_level,
        },
    )

    return AssertionResult(
        invariant=invariant,
        passed=True,
    )


register_assertion(
    invariant_id="INV-008",
    evaluator=evaluate_constrained_rehabilitation,
)
