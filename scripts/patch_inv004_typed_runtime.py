from pathlib import Path


ASSERTIONS_PATH = Path(
    "project/governance/validation/assertions.py"
)


content = ASSERTIONS_PATH.read_text()


OLD_BLOCK = '''
    governance_trace = runtime_context.get("governance_trace")

    active_modes = runtime_context.get(
        "governance_state",
        {}
    ).get(
        "active_modes",
        []
    )
'''


NEW_BLOCK = '''
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
'''


content = content.replace(
    OLD_BLOCK,
    NEW_BLOCK,
)


ASSERTIONS_PATH.write_text(content)

print(
    "INV-004 upgraded for typed runtime context support."
)
