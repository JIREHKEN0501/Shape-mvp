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
'''


NEW_BLOCK = '''
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
'''


content = content.replace(
    OLD_BLOCK,
    NEW_BLOCK,
)


ASSERTIONS_PATH.write_text(content)

print(
    "INV-008 upgraded for typed runtime context support."
)
