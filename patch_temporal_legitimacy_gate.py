from pathlib import Path

CONFIDENCE_FILE = Path(
    "project/app/services/routing/confidence_engine.py"
)

OLD_BLOCK = '''
    if history_depth >= TEMPORAL_MIN_HISTORY:

        oscillation_score = oscillation_state.get(
            "oscillation_score",
            0.0
        )

        temporal_consistency_contribution = max(
            0.0,
            0.25 - (oscillation_score * 0.25)
        )

    else:

        temporal_ceiling_active = True
'''

NEW_BLOCK = '''
    temporal_legitimacy_ready = (

        history_depth >= TEMPORAL_MIN_HISTORY

        and signal_density >= 1

        and readiness_score > 0
    )

    if temporal_legitimacy_ready:

        oscillation_score = oscillation_state.get(
            "oscillation_score",
            0.0
        )

        temporal_consistency_contribution = max(
            0.0,
            0.25 - (oscillation_score * 0.25)
        )

    else:

        temporal_ceiling_active = True
'''

def main():

    content = CONFIDENCE_FILE.read_text(
        encoding="utf-8"
    )

    if "temporal_legitimacy_ready" in content:

        print(
            "Temporal legitimacy gate already integrated."
        )

        return

    if OLD_BLOCK not in content:

        print(
            "Original temporal consistency block not found."
        )

        return

    content = content.replace(
        OLD_BLOCK,
        NEW_BLOCK
    )

    CONFIDENCE_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "Temporal legitimacy gate integrated."
    )


if __name__ == "__main__":
    main()
