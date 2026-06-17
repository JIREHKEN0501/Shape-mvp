from pathlib import Path

TARGET_FILE = Path(
    "project/app/services/routing/routing_trace_store.py"
)

OLD_BLOCK = '''
def persist_routing_trace(
    participant_id: str,
    trace: Dict[str, Any]
) -> None:
    """
    Persist routing transparency trace.

    IMPORTANT:
    Stored traces describe session-level routing behavior only.
    """

    payload = {
        "event_type": "routing_trace",

        "participant_id": participant_id,

        "timestamp": time.time(),

        "trace": trace
    }
'''

NEW_BLOCK = '''
def persist_routing_trace(
    participant_id: str,
    trace: Dict[str, Any],
    health: Dict[str, Any] | None = None
) -> None:
    """
    Persist routing transparency trace.

    IMPORTANT:
    Stored traces describe session-level routing behavior only.
    """

    payload = {
        "event_type": "routing_trace",

        "participant_id": participant_id,

        "timestamp": time.time(),

        "trace": trace
    }

    # =====================================
    # Optional orchestration health telemetry
    # =====================================

    if health is not None:

        payload["health"] = health
'''

def main():

    content = TARGET_FILE.read_text(
        encoding="utf-8"
    )

    if 'payload["health"]' in content:
        print("Health persistence already integrated.")
        return

    if OLD_BLOCK not in content:
        print("Target block not found.")
        return

    updated = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    TARGET_FILE.write_text(
        updated,
        encoding="utf-8"
    )

    print(
        "Routing trace health persistence integrated."
    )


if __name__ == "__main__":
    main()
