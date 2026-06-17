from pathlib import Path

TASKS_PATH = Path(
    "project/app/services/tasks.py"
)

text = TASKS_PATH.read_text(
    encoding="utf-8"
)

# =====================================================
# Inject governed adaptation import
# =====================================================

import_block = """
from project.app.services.routing.confidence_engine import (
    build_orchestration_confidence
)
"""

replacement_import_block = """
from project.app.services.routing.confidence_engine import (
    build_orchestration_confidence
)

from project.app.services.routing.governed_adaptation import (
    mediate_difficulty_adjustment
)

from project.governance.validation.governance_envelope import (
    GovernanceEnvelope
)
"""

if (
    "mediate_difficulty_adjustment"
    not in text
):
    text = text.replace(
        import_block,
        replacement_import_block
    )

# =====================================================
# Inject governance envelope synthesis
# =====================================================

target_block = """
    # =====================================
    # Governance-aware difficulty enforcement
    # =====================================
"""

governance_injection = """
    # =====================================
    # Governance envelope synthesis
    # =====================================

    governance_envelope = GovernanceEnvelope(

        governance_status=(
            governance_state.get(
                "governance_status",
                "stable"
            )
        ),

        topology_integrity=(
            governance_state.get(
                "topology_integrity",
                "stable"
            )
        ),

        authority_ceiling=(
            resolved_constraints.get(
                "authority_ceiling",
                1.0
            )
        ),

        reevaluation_required=(
            governance_state.get(
                "reevaluation_required",
                False
            )
        ),

        arbitration_active=(
            governance_state.get(
                "arbitration_active",
                False
            )
        ),

        active_constraints=(
            resolved_constraints.get(
                "active_constraints",
                []
            )
        ),
    )

    governed_adaptation = (
        mediate_difficulty_adjustment(

            base_difficulty=(
                base_difficulty
            ),

            proposed_difficulty=(
                chosen_difficulty
            ),

            governance_envelope=(
                governance_envelope
            ),
        )
    )

    chosen_difficulty = (
        governed_adaptation
        .permitted_difficulty
    )

    difficulty_adjustment = (
        chosen_difficulty
        - base_difficulty
    )

"""

if (
    "Governance envelope synthesis"
    not in text
):
    text = text.replace(
        target_block,
        governance_injection
        + target_block
    )

# =====================================================
# Inject orchestration explainability
# =====================================================

meta_target = """
            "confidence": orchestration_confidence
"""

meta_replacement = """
            "confidence": orchestration_confidence,

            "governed_adaptation": {
                "permitted_difficulty": (
                    governed_adaptation
                    .permitted_difficulty
                ),

                "escalation_constrained": (
                    governed_adaptation
                    .escalation_constrained
                ),

                "recovery_constrained": (
                    governed_adaptation
                    .recovery_constrained
                ),

                "governance_reason": (
                    governed_adaptation
                    .governance_reason
                ),
            }
"""

if (
    '"governed_adaptation"'
    not in text
):
    text = text.replace(
        meta_target,
        meta_replacement
    )

TASKS_PATH.write_text(
    text,
    encoding="utf-8"
)

print(
    "✅ Governed adaptation integration applied."
)
