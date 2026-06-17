from pathlib import Path

TRACE_FILE = Path(
    "project/app/services/routing/selection_trace.py"
)

OLD_BLOCK = '''
    final_selection_reason = (
        "Highest-ranked eligible task selected"
    )
'''

NEW_BLOCK = '''
    # =====================================
    # Final orchestration reasoning synthesis
    # =====================================

    reasoning_parts = []

    if category_deviation:

        reasoning_parts.append(

            f"{selected_category} selected "
            f"over {target_category}"
        )

    else:

        reasoning_parts.append(

            f"{selected_category} selected "
            "as target-aligned category"
        )

    if selection_reasons:

        reasoning_parts.append(
            selection_reasons[0]
        )

    if governance_influence:

        reasoning_parts.append(
            "under active governance constraints"
        )

    final_selection_reason = (
        ". ".join(reasoning_parts) + "."
    )
'''

def main():

    content = TRACE_FILE.read_text(
        encoding="utf-8"
    )

    if (
        'reasoning_parts = []'
        in content
    ):

        print(
            "Selection trace synthesis already updated."
        )

        return

    if OLD_BLOCK not in content:

        print(
            "Original selection reasoning block not found."
        )

        return

    content = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    TRACE_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Selection trace synthesis updated."
    )


if __name__ == "__main__":
    main()
