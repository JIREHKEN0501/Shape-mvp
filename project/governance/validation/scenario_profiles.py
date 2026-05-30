from dataclasses import dataclass

@dataclass
class LongitudinalScenarioProfile:
    """
    Explicit replay trajectory profile.

    Used when validation requires
    deterministic longitudinal behavior
    rather than pressure-driven emergence.
    """

    scenario_name: str

    instability_sequence: list[float]

    escalation_sequence: list[float]

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

# =====================================
# False Recovery Arc
# =====================================

FALSE_RECOVERY_PROFILE = (
    ScenarioPressureProfile(

        scenario_name=(
            "false_recovery_arc"
        ),

        escalation_growth_rate=0.20,

        instability_resistance=0.10,

        anticipatory_damping_strength=0.20,

        governance_responsiveness=0.20,

        recovery_persistence=0.24,

        critical_recovery_strength=0.32,
    )
)

# =====================================
# Explicit False Recovery Arc
# =====================================

FALSE_RECOVERY_TRAJECTORY = (
    LongitudinalScenarioProfile(

        scenario_name=(
            "false_recovery_trajectory"
        ),

        instability_sequence=[

            0.10,
            0.24,
            0.40,
            0.55,
            0.48,
            0.40,
            0.34,
            0.60,
            0.78,
            0.92,
        ],

        escalation_sequence=[

            0.10,
            0.18,
            0.26,
            0.32,
            0.24,
            0.18,
            0.12,
            0.42,
            0.60,
            0.80,
        ],
    )
)

# =====================================
# Oscillatory Recovery Arc
# =====================================

OSCILLATORY_RECOVERY_TRAJECTORY = (
    LongitudinalScenarioProfile(

        scenario_name=(
            "oscillatory_recovery_trajectory"
        ),

        instability_sequence=[

            0.10,
            0.24,
            0.40,
            0.32,
            0.50,
            0.36,
            0.58,
            0.42,
            0.64,
            0.48,
        ],

        escalation_sequence=[

            0.10,
            0.18,
            0.26,
            0.16,
            0.34,
            0.18,
            0.42,
            0.24,
            0.50,
            0.30,
        ],
    )
)

