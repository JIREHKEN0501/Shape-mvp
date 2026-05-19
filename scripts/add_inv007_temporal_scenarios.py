from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


content = TEST_PATH.read_text()


INSERT_BEFORE = '''
    {
        "name": "rehabilitation_overshoot_violation_state",
'''


TEMPORAL_SCENARIOS = '''
    {
        "name": (
            "temporal_reevaluation_compliant_state"
        ),

        "runtime_context": {
            "governance_state": {
                "active_modes": [
                    "stabilization"
                ],
                "authority_level": 0.5,
            },

            "temporal_state": {
                "reevaluation_required": True,
                "last_evaluation_at": (
                    "2026-05-19T15:00:00Z"
                ),
            },

            "governance_trace": {
                "routing_status": "restricted",
                "reasoning": [
                    "Periodic reevaluation active."
                ],
                "routing_directives": {
                    "stabilize": True
                },
                "transparency_note": (
                    "Governance reevaluation current."
                ),
            },
        },
    },

    {
        "name": (
            "temporal_reevaluation_overdue_state"
        ),

        "runtime_context": {
            "governance_state": {
                "active_modes": [
                    "suppression"
                ],
                "authority_level": 0.2,
            },

            "temporal_state": {
                "reevaluation_required": True,
                "last_evaluation_at": "",
            },

            "governance_trace": {
                "routing_status": "restricted",
                "reasoning": [
                    "Suppression active."
                ],
                "routing_directives": {
                    "suppress": True
                },
                "transparency_note": (
                    "Governance reevaluation overdue."
                ),
            },
        },
    },

'''


if "temporal_reevaluation_compliant_state" not in content:

    content = content.replace(
        INSERT_BEFORE,
        TEMPORAL_SCENARIOS + INSERT_BEFORE,
    )


TEST_PATH.write_text(content)

print(
    "INV-007 temporal governance scenarios added."
)
