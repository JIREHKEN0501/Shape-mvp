from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


NEW_SCENARIO = '''
    {
        "name": "legitimacy_inflation_violation_state",

        "runtime_context": {
            "governance_state": {
                "active_modes": [],
                "authority_level": 1.0,
            },

            "legitimacy_state": {
                "confidence": 0.95,
            },

            "evidence_state": {
                "evidence_score": 0.2,
            },

            "governance_trace": {
                "routing_status": "normal",
                "reasoning": [
                    "high confidence despite sparse evidence"
                ],
                "routing_directives": {},
                "transparency_note": (
                    "Legitimacy inflation test scenario."
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


if "legitimacy_inflation_violation_state" not in content:
    content = content.replace(
        marker,
        NEW_SCENARIO + marker,
    )

    TEST_PATH.write_text(content)

    print("INV-002 violation scenario added.")
else:
    print("Scenario already exists.")
