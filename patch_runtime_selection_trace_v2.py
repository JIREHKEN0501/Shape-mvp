from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

IMPORT_BLOCK = '''
from project.app.services.routing.constraint_resolver import (
    resolve_governance_constraints
)
'''

NEW_IMPORTS = '''
from project.app.services.routing.constraint_resolver import (
    resolve_governance_constraints
)

from project.app.services.routing.selection_trace import (
    build_selection_trace
)
'''

RAW_TASK_BLOCK = '''
    raw_task = random.choice(top_slice)
'''

NEW_RAW_TASK_BLOCK = '''
    raw_task = random.choice(top_slice)

    # =====================================
    # Build orchestration explainability
    # =====================================

    selection_trace = (
        build_selection_trace(

            target_category=chosen_category,

            selected_category=raw_task.get(
                "category",
                "unknown"
            ),

            selection_reasons=raw_task.get(
                "_selection_reasons",
                []
            ),

            difficulty_adjustment=difficulty_adjustment,

            governance_state=governance_state,

            resolved_constraints=resolved_constraints
        )
    )
'''

META_BLOCK = '''
            "resolved_constraints": resolved_constraints
'''

NEW_META_BLOCK = '''
            "resolved_constraints": resolved_constraints,
            "selection_trace": selection_trace
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if '"selection_trace": selection_trace' in content:

        print(
            "Runtime selection trace already integrated."
        )

        return

    if IMPORT_BLOCK not in content:

        print(
            "Constraint resolver import block not found."
        )

        return

    content = content.replace(
        IMPORT_BLOCK,
        NEW_IMPORTS
    )

    if RAW_TASK_BLOCK not in content:

        print(
            "Raw task selection block not found."
        )

        return

    content = content.replace(
        RAW_TASK_BLOCK,
        NEW_RAW_TASK_BLOCK
    )

    if META_BLOCK not in content:

        print(
            "Resolved constraints meta block not found."
        )

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
        "Runtime selection trace integrated."
    )


if __name__ == "__main__":
    main()
