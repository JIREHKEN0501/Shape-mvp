from pathlib import Path


INVARIANTS_PATH = Path(
    "project/governance/validation/invariants.py"
)


content = INVARIANTS_PATH.read_text()


INSERT_BEFORE = '''
}
        
        
def get_invariant(invariant_id: str) -> GovernanceInvariant | None:
'''


INV009_BLOCK = '''
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
'''


if '"INV-009"' not in content:

    content = content.replace(
        INSERT_BEFORE,
        INV009_BLOCK,
    )


INVARIANTS_PATH.write_text(content)

print(
    "INV-009 registered successfully."
)
