from project.governance.validation.longitudinal_simulation import (
    run_longitudinal_simulation,
    print_simulation_summary,
    generate_longitudinal_insights,
)
from project.governance.validation.oscillation_analysis import (
    classify_oscillation_behavior
)
from project.governance.validation.scenario_profiles import (
    STABILIZATION_PROFILE,
    PERSISTENT_ESCALATION_PROFILE,
    RECOVERY_PROFILE,
)

def main():

    SCENARIOS = [

        STABILIZATION_PROFILE,

        PERSISTENT_ESCALATION_PROFILE,

        RECOVERY_PROFILE,
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

if __name__ == "__main__":
    main()
