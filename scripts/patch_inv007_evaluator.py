from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


content = ASSERTIONS_PATH.read_text()


IMPORT_OLD = '''
from .constants import (
    FULL_AUTHORITY_LEVEL,
    HIGH_CONFIDENCE_THRESHOLD,
    SUFFICIENT_EVIDENCE_SCORE,
    HIGH_AUTHORITY_THRESHOLD,
)
'''


IMPORT_NEW = '''
from .constants import (
    FULL_AUTHORITY_LEVEL,
    HIGH_CONFIDENCE_THRESHOLD,
    SUFFICIENT_EVIDENCE_SCORE,
    HIGH_AUTHORITY_THRESHOLD,
    MAX_REEVALUATION_INTERVAL_SECONDS,
)
'''


content = content.replace(
    IMPORT_OLD,
    IMPORT_NEW,
)


INSERT_BEFORE = '''
def evaluate_constrained_rehabilitation(
'''


INV007_EVALUATOR = '''
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
'''


if "def evaluate_temporal_reevaluation_integrity" not in content:

    content = content.replace(
        INSERT_BEFORE,
        INV007_EVALUATOR,
    )


ASSERTIONS_PATH.write_text(content)

print(
    "INV-007 temporal reevaluation evaluator added."
)
