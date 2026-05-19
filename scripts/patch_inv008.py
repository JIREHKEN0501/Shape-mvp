from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


IMPORT_BLOCK = """
from .constants import (
    FULL_AUTHORITY_LEVEL,
    HIGH_CONFIDENCE_THRESHOLD,
    SUFFICIENT_EVIDENCE_SCORE,
    HIGH_AUTHORITY_THRESHOLD,
)
"""


INV008_BLOCK = '''

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
'''


content = ASSERTIONS_PATH.read_text()


if "HIGH_AUTHORITY_THRESHOLD" not in content:
    content = content.replace(
        "SUFFICIENT_EVIDENCE_SCORE,",
        "SUFFICIENT_EVIDENCE_SCORE,\n    HIGH_AUTHORITY_THRESHOLD,",
    )


if "evaluate_constrained_rehabilitation" not in content:
    content += INV008_BLOCK


ASSERTIONS_PATH.write_text(content)

print("INV-008 evaluator patch applied successfully.")
