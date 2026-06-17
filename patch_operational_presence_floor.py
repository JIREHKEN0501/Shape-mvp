from pathlib import Path

CONFIDENCE_FILE = Path(
    "project/app/services/routing/confidence_engine.py"
)

ANCHOR = '''
    # =====================================
    # Final confidence payload
    # =====================================
'''

INSERT_BLOCK = '''
    # =====================================
    # Operational presence floor
    # =====================================

    suppression_active = (
        "suppression" in governance_state.get(
            "active_modes",
            []
        )
    )

    if (

        confidence_score == 0.0

        and temporal_ceiling_active

        and not suppression_active
    ):

        confidence_score = 0.05

'''

NEW_BLOCK = INSERT_BLOCK + ANCHOR

def main():

    content = CONFIDENCE_FILE.read_text(
        encoding="utf-8"
    )

    if "Operational presence floor" in content:

        print(
            "Operational presence floor already integrated."
        )

        return

    if ANCHOR not in content:

        print(
            "Final payload anchor not found."
        )

        return

    content = content.replace(
        ANCHOR,
        NEW_BLOCK
    )

    CONFIDENCE_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Operational presence floor integrated."
    )


if __name__ == "__main__":
    main()
