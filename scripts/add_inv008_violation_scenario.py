from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


NEW_SCENARIO = '''
    {
        "name": "rehabilitation_overshoot_violation_state",

        "runtime_context": {
            "governance_state": {
                "active_modes": ["stabilization"],
                "authority_level": 0.95,
            },

            "legitimacy_state": {
                "rehabilitation_active": True,
            },

            "governance_trace": {
                "routing_status": "recovering",
                "reasoning": [
                    "rehabilitation progressing aggressively"
                ],
                "routing_directives": {
                    "rehabilitate": True
                },
                "transparency_note": (
                    "Rehabilitation overshoot test scenario."
                ),
            },
        },
    },

'''


content = TEST_PATH.read_text()


marker = '''
    {
        "name": "precedence_violation_state",
'''


if "rehabilitation_overshoot_violation_state" not in content:
    content = content.replace(
        marker,
        NEW_SCENARIO + marker,
    )

    TEST_PATH.write_text(content)

    print("INV-008 violation scenario added.")
else:
    print("Scenario already exists.")
