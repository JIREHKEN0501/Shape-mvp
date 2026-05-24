from project.governance.validation.longitudinal_simulation import (
    run_longitudinal_simulation,
    print_simulation_summary,
    generate_longitudinal_insights,
)


def main():

    states = run_longitudinal_simulation(
        total_cycles=10
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


if __name__ == "__main__":
    main()
