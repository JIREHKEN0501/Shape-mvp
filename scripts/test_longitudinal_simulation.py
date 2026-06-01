from project.governance.validation.longitudinal_simulation import (
    run_longitudinal_simulation,
    print_simulation_summary,
    generate_longitudinal_insights,
)
from project.governance.validation.oscillation_analysis import (
    classify_oscillation_behavior
)
from project.governance.validation.progression_interpreter import (
    interpret_progression_behavior
)
from project.governance.validation.scenario_profiles import (
    STABILIZATION_PROFILE,
    PERSISTENT_ESCALATION_PROFILE,
    RECOVERY_PROFILE,
    SUSTAINED_RECOVERY_PROFILE,
    AMBIGUOUS_RECOVERY_PROFILE,
    FALSE_RECOVERY_PROFILE,
    FALSE_RECOVERY_TRAJECTORY,
    OSCILLATORY_RECOVERY_TRAJECTORY,
    DELAYED_RECOVERY_TRAJECTORY,
)

def main():

    SCENARIOS = [

        STABILIZATION_PROFILE,

        PERSISTENT_ESCALATION_PROFILE,

        RECOVERY_PROFILE,

        SUSTAINED_RECOVERY_PROFILE,

        AMBIGUOUS_RECOVERY_PROFILE,

        FALSE_RECOVERY_PROFILE,

        FALSE_RECOVERY_TRAJECTORY,

        OSCILLATORY_RECOVERY_TRAJECTORY,

        DELAYED_RECOVERY_TRAJECTORY,
    ]

    for profile in SCENARIOS:

        print(
            "\n=================================="
        )

        print(
            f"SCENARIO: "
            f"{profile.scenario_name}"
        )

        print(
            "=================================="
        )

        states = (
            run_longitudinal_simulation(
                total_cycles=10,
                profile=profile,
            )
        )

        print_simulation_summary(states)

        print(
            "\n=== LONGITUDINAL INSIGHTS ===\n"
        )

        insights = (
            generate_longitudinal_insights(
                states
            )
        )

        for insight in insights:

            print(f"- {insight}")

        print(
            "\n=== OSCILLATION ANALYSIS ===\n"
        )

        analysis = (
            classify_oscillation_behavior(
                states
            )
        )

        interpretation = (
            interpret_progression_behavior(
                states,
                analysis,
            )
        )

        print(
            f"oscillation_pattern: "
            f"{analysis.oscillation_pattern}"
        )

        print(
            f"governance_transitions: "
            f"{analysis.governance_transitions}"
        )

        print(
            f"stabilization_cycles: "
            f"{analysis.stabilization_cycles}"
        )

        print(
            f"critical_cycles: "
            f"{analysis.critical_cycles}"
        )

        print(
            f"interpretation: "
            f"{analysis.interpretation}"
        )

        print(
            "\n=== PROGRESSION INTERPRETATION ===\n"
        )

        print(
            f"narrative_archetype: "
            f"{interpretation.narrative_archetype}"
        )

        print(
            f"interpretation_confidence: "
            f"{interpretation.interpretation_confidence}"
        )

        print(
            "\nprogression_summary:\n"
        )

        print(
            interpretation.progression_summary
        )

if __name__ == "__main__":
    main()
