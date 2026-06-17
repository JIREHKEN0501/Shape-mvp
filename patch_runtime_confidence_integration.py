from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

IMPORT_BLOCK = '''
from project.app.services.routing.selection_trace import (
    build_selection_trace
)
'''

NEW_IMPORTS = '''
from project.app.services.routing.selection_trace import (
    build_selection_trace
)

from project.app.services.routing.confidence_engine import (
    build_orchestration_confidence
)
'''

SELECTION_TRACE_BLOCK = '''
    selection_trace = (
        build_selection_trace(

            target_category=chosen_category,

            selected_category=raw_task.get(
                "category",
                "unknown"
            ),

            selection_reasons=selection_reasons,

            difficulty_adjustment=difficulty_adjustment,

            governance_state=governance_state,

            resolved_constraints=resolved_constraints
        )
    )
'''

NEW_SELECTION_TRACE_BLOCK = '''
    selection_trace = (
        build_selection_trace(

            target_category=chosen_category,

            selected_category=raw_task.get(
                "category",
                "unknown"
            ),

            selection_reasons=selection_reasons,

            difficulty_adjustment=difficulty_adjustment,

            governance_state=governance_state,

            resolved_constraints=resolved_constraints
        )
    )

    # =====================================
    # Build orchestration confidence
    # =====================================

    orchestration_confidence = (
        build_orchestration_confidence(

            orchestration_health=orchestration_health,

            governance_state=governance_state,

            oscillation_state=oscillation_state,

            history_depth=len(history)
        )
    )
'''

META_BLOCK = '''
            "selection_trace": selection_trace
'''

NEW_META_BLOCK = '''
            "selection_trace": selection_trace,
            "confidence": orchestration_confidence
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if '"confidence": orchestration_confidence' in content:

        print(
            "Runtime confidence already integrated."
        )

        return

    if IMPORT_BLOCK not in content:

        print(
            "Selection trace import block not found."
        )

        return

    content = content.replace(
        IMPORT_BLOCK,
        NEW_IMPORTS
    )

    if SELECTION_TRACE_BLOCK not in content:

        print(
            "Selection trace block not found."
        )

        return

    content = content.replace(
        SELECTION_TRACE_BLOCK,
        NEW_SELECTION_TRACE_BLOCK
    )

    if META_BLOCK not in content:

        print(
            "Selection trace meta block not found."
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
        "Runtime confidence integration complete."
    )


if __name__ == "__main__":
    main()
