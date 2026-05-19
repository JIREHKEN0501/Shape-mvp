from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


content = ASSERTIONS_PATH.read_text()


IMPORT_OLD = '''
from .violations import GovernanceViolation
'''


IMPORT_NEW = '''
from .violations import GovernanceViolation
from .runtime_schema import RuntimeGovernanceContext
'''


if "RuntimeGovernanceContext" not in content:

    content = content.replace(
        IMPORT_OLD,
        IMPORT_NEW,
    )


OLD_BLOCK = '''
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
'''


NEW_BLOCK = '''
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
'''


content = content.replace(
    OLD_BLOCK,
    NEW_BLOCK,
)


ASSERTIONS_PATH.write_text(content)

print(
    "INV-001 upgraded for typed runtime context support."
)
