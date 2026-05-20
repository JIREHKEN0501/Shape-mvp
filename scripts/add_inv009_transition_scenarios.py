from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


content = TEST_PATH.read_text()


INSERT_BEFORE = '''
    {
        "name": (
            "temporal_reevaluation_compliant_state"
'''


INV009_SCENARIOS = '''
    {
        "name": (
            "legal_transition_progression"
        ),

        "runtime_context": {
            "governance_state": {
                "previous_state": (
                    "suppression"
                ),
                "current_state": (
                    "stabilization"
                ),
                "active_modes": [
                    "stabilization"
                ],
                "authority_level": 0.4,
            },

            "governance_trace": {
                "routing_status": (
                    "restricted"
                ),
                "reasoning": [
                    "Progressive recovery active."
                ],
                "routing_directives": {
                    "stabilize": True
                },
                "transparency_note": (
                    "Transition legality valid."
                ),
            },
        },
    },

    {
        "name": (
            "illegal_transition_bypass"
        ),

        "runtime_context": {
            "governance_state": {
                "previous_state": (
                    "suppression"
                ),
                "current_state": (
                    "unrestricted"
                ),
                "active_modes": [],
                "authority_level": 1.0,
            },

            "governance_trace": {
                "routing_status": (
                    "unrestricted"
                ),
                "reasoning": [
                    "Authority restored abruptly."
                ],
                "routing_directives": {},
                "transparency_note": (
                    "Illegal restoration bypass."
                ),
            },
        },
    },

'''


if "legal_transition_progression" not in content:

    content = content.replace(
        INSERT_BEFORE,
        INV009_SCENARIOS + INSERT_BEFORE,
    )


TEST_PATH.write_text(content)

print(
    "INV-009 transition legality scenarios added."
)
