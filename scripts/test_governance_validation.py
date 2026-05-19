from pprint import pprint

from project.governance.validation.assertions import (
    evaluate_all_assertions,
)
from project.governance.validation.telemetry import (
    telemetry_buffer,
)

from project.governance.validation.reporting import (
    generate_validation_report,
)


test_scenarios = [
    {
        "name": "normal_unrestricted_orchestration",

        "runtime_context": {
            "governance_state": {
                "active_modes": [],
                "authority_level": 1.0,
            },

            "governance_trace": {
                "routing_status": "normal",
                "reasoning": [
                    "normal orchestration"
                ],
                "routing_directives": {},
                "transparency_note": (
                    "No governance restrictions active."
                ),
            },
        },
    },

    {
        "name": "bounded_low_authority_state",

        "runtime_context": {
            "governance_state": {
                "active_modes": ["low_authority"],
                "authority_level": 0.7,
            },

            "governance_trace": {
                "routing_status": "bounded",
                "reasoning": [
                    "authority constrained"
                ],
                "routing_directives": {
                    "limit_authority": True
                },
                "transparency_note": (
                    "Partial authority restriction active."
                ),
            },
        },
    },

    {
        "name": "suppression_containment_state",

        "runtime_context": {
            "governance_state": {
                "active_modes": ["suppression"],
                "authority_level": 0.2,
            },

            "governance_trace": {
                "routing_status": "suppressed",
                "reasoning": [
                    "suppression active"
                ],
                "routing_directives": {
                    "suppress": True
                },
                "transparency_note": (
                    "Suppression containment active."
                ),
            },
        },
    },

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


    {
        "name": "precedence_violation_state",

        "runtime_context": {
            "governance_state": {
                "active_modes": ["stabilization"],
                "authority_level": 1.0,
            },

            "governance_trace": {
                "routing_status": "restricted",
                "reasoning": [
                    "stabilization active"
                ],
                "routing_directives": {
                    "stabilize": True
                },
                "transparency_note": (
                    "Governance stabilization active."
                ),
            },
        },
    },
]


for scenario in test_scenarios:

    print(f"\n=== SCENARIO: {scenario['name']} ===\n")

    telemetry_buffer.clear()

    results = evaluate_all_assertions(
        scenario["runtime_context"]
    )

    print("\n--- ASSERTION RESULTS ---\n")

    for result in results:
        pprint({
            "invariant": result.invariant.invariant_id,
            "passed": result.passed,
            "violations": [
                violation.to_dict()
                for violation in result.violations
            ],
        })


    report = generate_validation_report(results)

    print("\n--- GOVERNANCE REPORT ---\n")

    pprint({
        "governance_status": report.governance_status,
        "total_assertions": report.total_assertions,
        "passed_assertions": report.passed_assertions,
        "failed_assertions": report.failed_assertions,
        "severity_counts": report.severity_counts,
    })

    print("\n--- TELEMETRY EVENTS ---\n")

    for event in telemetry_buffer.list_events():
        pprint(event.to_dict())
