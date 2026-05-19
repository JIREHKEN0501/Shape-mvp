from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


content = ASSERTIONS_PATH.read_text()


OLD_BLOCK = '''
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
'''


NEW_BLOCK = '''
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
'''


content = content.replace(
    OLD_BLOCK,
    NEW_BLOCK,
)


ASSERTIONS_PATH.write_text(content)

print(
    "INV-002 upgraded for typed runtime context support."
)
