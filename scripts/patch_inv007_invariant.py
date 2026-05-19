from pathlib import Path


INVARIANTS_PATH = Path(
    "project/governance/validation/invariants.py"
)


content = INVARIANTS_PATH.read_text()


INSERT_AFTER = '''
    register_invariant(
        GovernanceInvariant(
            invariant_id="INV-008",
'''


INV007_BLOCK = '''
    register_invariant(
        GovernanceInvariant(
            invariant_id="INV-007",
            name=(
                "Governance Reevaluation Must Remain "
                "Time-Sensitive"
            ),
            description=(
                "Governance states must not persist "
                "indefinitely without reevaluation."
            ),
            severity="major",
        )
    )

'''

if 'invariant_id="INV-007"' not in content:

    content = content.replace(
        INSERT_AFTER,
        INV007_BLOCK + INSERT_AFTER,
    )


INVARIANTS_PATH.write_text(content)

print(
    "INV-007 invariant registered."
)
