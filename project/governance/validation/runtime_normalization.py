from typing import Any, Dict

from .runtime_schema import (
    RuntimeGovernanceContext,
    GovernanceState,
    EvidenceState,
    LegitimacyState,
    GovernanceTrace,
    TemporalGovernanceState,
)


def normalize_runtime_context(
    runtime_context: Any,
) -> RuntimeGovernanceContext:
    """
    Normalize arbitrary runtime governance payloads
    into canonical RuntimeGovernanceContext form.
    """

    if isinstance(
        runtime_context,
        RuntimeGovernanceContext,
    ):
        return runtime_context

    if not isinstance(runtime_context, dict):
        raise TypeError(
            "Runtime context must be dict-like or "
            "RuntimeGovernanceContext."
        )

    governance_state_data = runtime_context.get(
        "governance_state",
        {}
    )

    evidence_state_data = runtime_context.get(
        "evidence_state",
        {}
    )

    legitimacy_state_data = runtime_context.get(
        "legitimacy_state",
        {}
    )

    governance_trace_data = runtime_context.get(
        "governance_trace",
        {}
    )

    temporal_state_data = runtime_context.get(
        "temporal_state",
        {}
    )

    return RuntimeGovernanceContext(

        governance_state=GovernanceState(
            active_modes=governance_state_data.get(
                "active_modes",
                [],
            ),
            authority_level=governance_state_data.get(
                "authority_level",
                1.0,
            ),
            escalation_level=governance_state_data.get(
                "escalation_level",
                0,
            ),
        ),

        evidence_state=EvidenceState(
            evidence_score=evidence_state_data.get(
                "evidence_score",
                0.0,
            ),
            evidence_sufficient=evidence_state_data.get(
                "evidence_sufficient",
                False,
            ),
        ),

        legitimacy_state=LegitimacyState(
            confidence=legitimacy_state_data.get(
                "confidence",
                0.0,
            ),
            legitimacy_established=(
                legitimacy_state_data.get(
                    "legitimacy_established",
                    False,
                )
            ),
            rehabilitation_active=(
                legitimacy_state_data.get(
                    "rehabilitation_active",
                    False,
                )
            ),
        ),

        governance_trace=GovernanceTrace(
            routing_status=governance_trace_data.get(
                "routing_status",
                "unknown",
            ),
            reasoning=governance_trace_data.get(
                "reasoning",
                [],
            ),
            routing_directives=(
                governance_trace_data.get(
                    "routing_directives",
                    {},
                )
            ),
            transparency_note=(
                governance_trace_data.get(
                    "transparency_note",
                    "",
                )
            ),
        ),

        temporal_state=TemporalGovernanceState(
            governance_state_entered_at=(
                temporal_state_data.get(
                    "governance_state_entered_at",
                    "",
                )
            ),
            last_evaluation_at=(
                temporal_state_data.get(
                    "last_evaluation_at",
                    "",
                )
            ),
            reevaluation_required=(
                temporal_state_data.get(
                    "reevaluation_required",
                    False,
                )
            ),
        ),

        metadata=runtime_context.get(
            "metadata",
            {},
        ),
    )
