from project.governance.validation.assertions import (
    evaluate_assertion,
)


def test_runtime_governance_state_passes_restriction_precedence():
    """
    Prove that a restrictive runtime governance state is accepted
    by the constitutional restriction-precedence invariant.
    """

    runtime_context = {
        "governance_state": {
            "active_modes": [
                "low_authority",
                "stabilization",
                "suppression",
            ],
            "authority_level": 0.2,
        }
    }

    result = evaluate_assertion(
        "INV-001",
        runtime_context,
    )

    assert result.passed is True
    assert result.violations == []


def test_runtime_governance_state_rejects_unrestricted_restoration():
    """
    Prove that restrictive runtime governance modes cannot coexist
    with unrestricted authority restoration.
    """

    runtime_context = {
        "governance_state": {
            "active_modes": [
                "stabilization",
                "suppression",
            ],
            "authority_level": 1.0,
        }
    }

    result = evaluate_assertion(
        "INV-001",
        runtime_context,
    )

    assert result.passed is False
    assert len(result.violations) == 1

    violation = result.violations[0]

    assert (
        violation.invariant.invariant_id
        == "INV-001"
    )
    assert (
        "Restrictive governance modes active"
        in violation.message
    )

def test_runtime_governance_trace_passes_visibility_invariant():
    """
    Prove that runtime governance state and routing trace remain
    constitutionally observable.
    """

    runtime_context = {
        "governance_state": {
            "active_modes": [
                "low_authority",
                "stabilization",
                "suppression",
            ],
            "authority_level": 0.2,
        },
        "governance_trace": {
            "routing_status": "resolved",
            "reasoning": [
                "Governance constraints applied",
            ],
            "routing_directives": {
                "reduce_difficulty": True,
            },
            "transparency_note": (
                "Routing behavior constrained by "
                "active governance state."
            ),
        },
    }

    result = evaluate_assertion(
        "INV-004",
        runtime_context,
    )

    assert result.passed is True
    assert result.violations == []


def test_missing_runtime_governance_trace_fails_visibility_invariant():
    """
    Prove that active governance without an observable routing
    trace is rejected by the constitutional visibility invariant.
    """

    runtime_context = {
        "governance_state": {
            "active_modes": [
                "stabilization",
                "suppression",
            ],
            "authority_level": 0.2,
        },
        "governance_trace": {},
    }

    result = evaluate_assertion(
        "INV-004",
        runtime_context,
    )

    assert result.passed is False
    assert len(result.violations) == 1

    violation = result.violations[0]

    assert (
        violation.invariant.invariant_id
        == "INV-004"
    )
    assert (
        "Governance trace missing"
        in violation.message
    )
