from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

IMPORT_BLOCK = '''
from project.app.services.routing.governance_state import (
    build_governance_state
)
'''

NEW_IMPORTS = '''
from project.app.services.routing.governance_state import (
    build_governance_state
)

from project.app.services.routing.constraint_resolver import (
    resolve_governance_constraints
)
'''

GOVERNANCE_BLOCK = '''
    governance_state = (
        build_governance_state(
            oscillation_state
        )
    )

    persist_routing_trace(
        participant_id,
        routing_trace,
        orchestration_health
    )
'''

NEW_GOVERNANCE_BLOCK = '''
    governance_state = (
        build_governance_state(
            oscillation_state
        )
    )

    # =====================================
    # Resolve governance constraints
    # =====================================

    resolved_constraints = (
        resolve_governance_constraints(
            governance_state
        )
    )

    persist_routing_trace(
        participant_id,
        routing_trace,
        orchestration_health
    )
'''

ROUTING_BLOCK = '''
    difficulty_adjustment = (
        chosen_difficulty - base_difficulty
    )
'''

NEW_ROUTING_BLOCK = '''
    difficulty_adjustment = (
        chosen_difficulty - base_difficulty
    )

    # =====================================
    # Governance-aware difficulty enforcement
    # =====================================

    max_shift = resolved_constraints.get(
        "max_difficulty_shift"
    )

    if max_shift == 0:

        chosen_difficulty = base_difficulty

    elif (
        max_shift == 1
        and abs(
            chosen_difficulty - base_difficulty
        ) > 1
    ):

        if chosen_difficulty > base_difficulty:

            chosen_difficulty = (
                base_difficulty + 1
            )

        else:

            chosen_difficulty = (
                base_difficulty - 1
            )

    difficulty_adjustment = (
        chosen_difficulty - base_difficulty
    )
'''

META_BLOCK = '''
            "governance_state": governance_state
'''

NEW_META_BLOCK = '''
            "governance_state": governance_state,
            "resolved_constraints": resolved_constraints
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if '"resolved_constraints": resolved_constraints' in content:

        print(
            "Runtime governance enforcement already integrated."
        )

        return

    if IMPORT_BLOCK not in content:

        print("Governance import block not found.")
        return

    content = content.replace(
        IMPORT_BLOCK,
        NEW_IMPORTS
    )

    if GOVERNANCE_BLOCK not in content:

        print("Governance runtime block not found.")
        return

    content = content.replace(
        GOVERNANCE_BLOCK,
        NEW_GOVERNANCE_BLOCK
    )

    # Replace ONLY first occurrence
    if ROUTING_BLOCK not in content:

        print("Difficulty adjustment block not found.")
        return

    content = content.replace(
        ROUTING_BLOCK,
        NEW_ROUTING_BLOCK,
        1
    )

    if META_BLOCK not in content:

        print("Governance meta block not found.")
        return

    content = content.replace(
        META_BLOCK,
        NEW_META_BLOCK
    )

    TASKS_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Runtime governance enforcement integrated."
    )


if __name__ == "__main__":
    main()
