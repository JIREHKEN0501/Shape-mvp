from dataclasses import dataclass


@dataclass
class ScenarioPressureProfile:
    """
    Defines longitudinal pressure semantics
    for governance validation scenarios.
    """

    scenario_name: str

    escalation_growth_rate: float

    instability_resistance: float

    anticipatory_damping_strength: float

    governance_responsiveness: float

    recovery_persistence: float

    critical_recovery_strength: float

# =====================================
# Stabilization Arc
# =====================================

STABILIZATION_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "stabilization_arc"
        ),

        escalation_growth_rate=0.12,

        instability_resistance=0.04,

        anticipatory_damping_strength=0.08,

        governance_responsiveness=0.08,

        recovery_persistence=0.10,

        critical_recovery_strength=0.20,
    )
)


# =====================================
# Persistent Escalation Arc
# =====================================

PERSISTENT_ESCALATION_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "persistent_escalation_arc"
        ),

        escalation_growth_rate=0.18,

        instability_resistance=0.10,

        anticipatory_damping_strength=0.03,

        governance_responsiveness=0.05,

        recovery_persistence=0.03,

        critical_recovery_strength=0.08,
    )
)


# =====================================
# Recovery Arc
# =====================================

RECOVERY_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "recovery_arc"
        ),

        escalation_growth_rate=0.20,

        instability_resistance=0.12,

        anticipatory_damping_strength=0.10,

        governance_responsiveness=0.12,

        recovery_persistence=0.15,

        critical_recovery_strength=0.30,
    )
)

# =====================================
# Sustained Recovery Arc
# =====================================

SUSTAINED_RECOVERY_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "sustained_recovery_arc"
        ),

        escalation_growth_rate=0.08,

        instability_resistance=0.10,

        anticipatory_damping_strength=0.20,

        governance_responsiveness=0.20,

        recovery_persistence=0.32,

        critical_recovery_strength=0.48,
    )
)

# =====================================
# Ambiguous Recovery Arc
# =====================================

AMBIGUOUS_RECOVERY_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "ambiguous_recovery_arc"
        ),

        escalation_growth_rate=0.12,

        instability_resistance=0.09,

        anticipatory_damping_strength=0.14,

        governance_responsiveness=0.15,

        recovery_persistence=0.18,

        critical_recovery_strength=0.26,
    )
)
