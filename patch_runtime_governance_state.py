from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

IMPORT_BLOCK = '''
from project.app.services.routing.oscillation_detector import (
    detect_orchestration_oscillation
)
'''

NEW_IMPORTS = '''
from project.app.services.routing.oscillation_detector import (
    detect_orchestration_oscillation
)

from project.app.services.routing.governance_state import (
    build_governance_state
)
'''

OSCILLATION_BLOCK = '''
    oscillation_state = (
        detect_orchestration_oscillation(
            orchestration_history
        )
    )

    persist_routing_trace(
        participant_id,
        routing_trace,
        orchestration_health
    )
'''

NEW_OSCILLATION_BLOCK = '''
    oscillation_state = (
        detect_orchestration_oscillation(
            orchestration_history
        )
    )

    # =====================================
    # Governance-state representation
    # =====================================

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

META_BLOCK = '''
            "health": orchestration_health,
            "oscillation": oscillation_state
'''

NEW_META_BLOCK = '''
            "health": orchestration_health,
            "oscillation": oscillation_state,
            "governance_state": governance_state
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if '"governance_state": governance_state' in content:

        print(
            "Governance-state runtime already integrated."
        )

        return

    if IMPORT_BLOCK not in content:

        print("Oscillation import block not found.")

        return

    content = content.replace(
        IMPORT_BLOCK,
        NEW_IMPORTS
    )

    if OSCILLATION_BLOCK not in content:

        print("Oscillation runtime block not found.")

        return

    content = content.replace(
        OSCILLATION_BLOCK,
        NEW_OSCILLATION_BLOCK
    )

    if META_BLOCK not in content:

        print("Meta orchestration block not found.")

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
        "Runtime governance-state integration successful."
    )


if __name__ == "__main__":
    main()
