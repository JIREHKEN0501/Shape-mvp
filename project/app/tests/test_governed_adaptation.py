from project.app.services.routing.governed_adaptation import (
    mediate_difficulty_adjustment,
)
from project.governance.validation.governance_envelope import (
    GovernanceEnvelope,
)


def make_envelope(**overrides):
    values = {
        "governance_status": "stable",
        "topology_integrity": "stable",
        "authority_ceiling": 1.0,
        "reevaluation_required": False,
        "arbitration_active": False,
    }

    values.update(overrides)

    return GovernanceEnvelope(**values)


def test_final_difficulty_is_bounded_to_canonical_range():
    cases = [
        (1, 1, 1),
        (1, 2, 2),
        (1, 3, 3),
        (1, 4, 3),
        (1, 99, 3),
        (3, 0, 1),
        (3, -10, 1),
    ]

    for base, proposed, expected in cases:
        result = mediate_difficulty_adjustment(
            base_difficulty=base,
            proposed_difficulty=proposed,
            governance_envelope=make_envelope(),
        )

        assert result.permitted_difficulty == expected
        assert 1 <= result.permitted_difficulty <= 3


def test_arbitration_constrains_aggressive_escalation():
    result = mediate_difficulty_adjustment(
        base_difficulty=1,
        proposed_difficulty=3,
        governance_envelope=make_envelope(
            arbitration_active=True,
        ),
    )

    assert result.permitted_difficulty == 2
    assert result.escalation_constrained is True


def test_low_authority_constrains_escalation():
    result = mediate_difficulty_adjustment(
        base_difficulty=1,
        proposed_difficulty=3,
        governance_envelope=make_envelope(
            authority_ceiling=0.4,
        ),
    )

    assert result.permitted_difficulty == 2
    assert result.escalation_constrained is True


def test_reevaluation_constrains_recovery_intensity():
    result = mediate_difficulty_adjustment(
        base_difficulty=3,
        proposed_difficulty=1,
        governance_envelope=make_envelope(
            reevaluation_required=True,
        ),
    )

    assert result.permitted_difficulty == 2
    assert result.recovery_constrained is True


def test_unstable_topology_blocks_escalation():
    result = mediate_difficulty_adjustment(
        base_difficulty=1,
        proposed_difficulty=2,
        governance_envelope=make_envelope(
            topology_integrity="unstable",
        ),
    )

    assert result.permitted_difficulty == 1
    assert result.escalation_constrained is True
