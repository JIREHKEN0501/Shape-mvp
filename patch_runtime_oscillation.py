from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

IMPORT_BLOCK = '''
from project.app.services.routing.orchestration_health import (
    evaluate_orchestration_health
)
'''

NEW_IMPORTS = '''
from project.app.services.routing.orchestration_health import (
    evaluate_orchestration_health
)

from project.app.services.routing.routing_history_loader import (
    load_recent_orchestration_history
)

from project.app.services.routing.oscillation_detector import (
    detect_orchestration_oscillation
)
'''

RUNTIME_BLOCK = '''
    orchestration_health = (
        evaluate_orchestration_health(
            normalized_signals,
            resolved_routing
        )
    )

    persist_routing_trace(
        participant_id,
        routing_trace,
        orchestration_health
    )
'''

NEW_RUNTIME = '''
    orchestration_health = (
        evaluate_orchestration_health(
            normalized_signals,
            resolved_routing
        )
    )

    # =====================================
    # Longitudinal orchestration instability
    # =====================================

    orchestration_history = (
        load_recent_orchestration_history(
            participant_id
        )
    )

    orchestration_history.append({

        "trace": routing_trace,

        "health": orchestration_health
    })

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

META_BLOCK = '''
        "orchestration": {
            "resolved_routing": resolved_routing,
            "routing_trace": routing_trace,
            "health": orchestration_health
        }
'''

NEW_META = '''
        "orchestration": {
            "resolved_routing": resolved_routing,
            "routing_trace": routing_trace,
            "health": orchestration_health,
            "oscillation": oscillation_state
        }
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if '"oscillation": oscillation_state' in content:

        print(
            "Runtime oscillation already integrated."
        )

        return

    if IMPORT_BLOCK not in content:

        print("Import block not found.")
        return

    content = content.replace(
        IMPORT_BLOCK,
        NEW_IMPORTS
    )

    if RUNTIME_BLOCK not in content:

        print("Runtime orchestration block not found.")
        return

    content = content.replace(
        RUNTIME_BLOCK,
        NEW_RUNTIME
    )

    if META_BLOCK not in content:

        print("Meta orchestration block not found.")
        return

    content = content.replace(
        META_BLOCK,
        NEW_META
    )

    TASKS_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Runtime oscillation integration successful."
    )


if __name__ == "__main__":
    main()
