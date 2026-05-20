from pathlib import Path


INVARIANTS_PATH = Path(
    "project/governance/validation/invariants.py"
)


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


# =====================================
# Register invariant
# =====================================

invariants_content = (
    INVARIANTS_PATH.read_text()
)


INSERT_BEFORE = '''
    register_invariant(
        GovernanceInvariant(
            invariant_id="INV-008",
'''


INV009_BLOCK = '''
    register_invariant(
        GovernanceInvariant(
            invariant_id="INV-009",
            name=(
                "Governance Transition Legality"
            ),
            description=(
                "Governance transitions must "
                "follow canonical topology legality."
            ),
            severity="critical",
        )
    )

'''


if 'invariant_id="INV-009"' not in invariants_content:

    invariants_content = invariants_content.replace(
        INSERT_BEFORE,
        INV009_BLOCK + INSERT_BEFORE,
    )


INVARIANTS_PATH.write_text(
    invariants_content
)


# =====================================
# Add assertion
# =====================================

assertions_content = (
    ASSERTIONS_PATH.read_text()
)


IMPORT_OLD = '''
from .runtime_normalization import (
    normalize_runtime_context,
)
'''


IMPORT_NEW = '''
from .runtime_normalization import (
    normalize_runtime_context,
)

from .topology_validation import (
    is_transition_allowed,
)
'''


assertions_content = assertions_content.replace(
    IMPORT_OLD,
    IMPORT_NEW,
)


INSERT_BEFORE_ASSERTION = '''
def evaluate_temporal_reevaluation_integrity(
'''


INV009_ASSERTION = '''
def evaluate_transition_legality(
    runtime_context: Dict[str, Any],
) -> AssertionResult:
    """
    Validate governance transition legality.
    """

    invariant = get_invariant("INV-009")

    if invariant is None:
        raise ValueError(
            "INV-009 invariant not registered."
        )

    governance_state = (
        runtime_context.governance_state
    )

    previous_state = (
        governance_state.previous_state
    )

    current_state = (
        governance_state.current_state
    )

    if previous_state:

        allowed = is_transition_allowed(
            previous_state,
            current_state,
        )

        if not allowed:

            violation = GovernanceViolation(
                invariant=invariant,
                message=(
                    "Illegal governance transition "
                    "detected."
                ),
                status=ViolationStatus.DETECTED,
                recommendation=(
                    "Ensure governance transitions "
                    "follow canonical topology."
                ),
                metadata={
                    "previous_state": (
                        previous_state
                    ),
                    "current_state": (
                        current_state
                    ),
                },
            )

            telemetry_buffer.emit(
                event_type=(
                    "transition_legality_violation"
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
            "transition_legality_verified"
        ),
        payload={
            "invariant_id": (
                invariant.invariant_id
            ),
            "previous_state": (
                previous_state
            ),
            "current_state": (
                current_state
            ),
        },
    )

    return AssertionResult(
        invariant=invariant,
        passed=True,
    )


register_assertion(
    invariant_id="INV-009",
    evaluator=evaluate_transition_legality,
)


def evaluate_temporal_reevaluation_integrity(
'''


if "def evaluate_transition_legality" not in assertions_content:

    assertions_content = assertions_content.replace(
        INSERT_BEFORE_ASSERTION,
        INV009_ASSERTION,
    )


ASSERTIONS_PATH.write_text(
    assertions_content
)


print(
    "INV-009 transition legality assertion added."
)
