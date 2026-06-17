from pathlib import Path

TASKS_FILE = Path(
    "project/app/services/tasks.py"
)

OLD_BLOCK = '''
    persist_routing_trace(
        participant_id,
        routing_trace
    )
'''

NEW_BLOCK = '''
    persist_routing_trace(
        participant_id,
        routing_trace,
        orchestration_health
    )
'''

def main():

    content = TASKS_FILE.read_text(
        encoding="utf-8"
    )

    if (
        "routing_trace,\n        orchestration_health"
        in content
    ):

        print(
            "Runtime health persistence already integrated."
        )

        return

    if OLD_BLOCK not in content:

        print("Target persistence block not found.")

        return

    updated = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    TASKS_FILE.write_text(
        updated,
        encoding="utf-8"
    )

    print(
        "Runtime orchestration health persistence integrated."
    )


if __name__ == "__main__":
    main()
