from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


IMPORT_BLOCK = """
from .constants import (
    FULL_AUTHORITY_LEVEL,
    HIGH_CONFIDENCE_THRESHOLD,
    SUFFICIENT_EVIDENCE_SCORE,
)
"""


INV002_BLOCK = '''

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
'''


content = ASSERTIONS_PATH.read_text()


if "HIGH_CONFIDENCE_THRESHOLD" not in content:
    content = content.replace(
        "from .constants import FULL_AUTHORITY_LEVEL",
        IMPORT_BLOCK.strip(),
    )


if "evaluate_persistence_legitimacy" not in content:
    content += INV002_BLOCK


ASSERTIONS_PATH.write_text(content)

print("INV-002 evaluator patch applied successfully.")
