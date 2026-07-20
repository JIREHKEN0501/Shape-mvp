
"""
Construction of immutable EvidenceContext objects from routing signals.

The EvidenceBuilder transforms normalized routing signals into structured
evidence domains consumed by the ADR-009 routing pipeline.
"""

from __future__ import annotations

import logging

from .evidence import (
    EvidenceContext,
    EvidenceObservation,
    GovernanceEvidence,
    PatternEvidence,
    PredictionEvidence,
    TemporalEvidence,
)
from .signal_schema import RoutingSignal
from typing import Final

logger = logging.getLogger(__name__)


class EvidenceBuilder:
    """
    Transforms normalized RoutingSignals into an immutable 
    EvidenceContext for downstream routing evaluation.
    """

    SIGNAL_DOMAINS: Final = {
        "fatigue_risk": "temporal",
        "latency_trend": "temporal",
        "confidence_trend": "temporal",
        "accuracy_trend": "temporal",

        "likely_response_style": "prediction",
        "risk_under_time_pressure": "prediction",

        "behavior_pattern": "pattern",
    }

    def build(
        self,
        signals: list[RoutingSignal],
    ) -> EvidenceContext:

        temporal = []
        prediction = []
        pattern = []
        governance = []

        for signal in signals:

            metadata = signal.metadata or {}

            observation = EvidenceObservation(
                kind=signal.signal_type,
                value=signal.value,
                confidence=signal.confidence,
                priority=signal.priority,
                source=signal.source,
                evidence_class=metadata.get("evidence_class"),
                dependencies=tuple(
                    metadata.get("dependencies", [])
                ),
                independent_observations=tuple(
                    metadata.get(
                        "independent_observations",
                        [],
                    )
                ),
            )

            domain = self.SIGNAL_DOMAINS.get(signal.signal_type)

            if domain == "temporal":
                temporal.append(observation)

            elif domain == "prediction":
                prediction.append(observation)

            elif domain == "pattern":
                pattern.append(observation)

            elif domain == "governance":
                governance.append(observation)

            else:
                logger.warning(
                    "Unrecognized routing signal '%s' ignored during evidence construction.",
                    signal.signal_type,
                )

        return EvidenceContext(
            temporal=TemporalEvidence(
                observations=tuple(temporal)
            ),
            prediction=PredictionEvidence(
                observations=tuple(prediction)
            ),
            pattern=PatternEvidence(
                observations=tuple(pattern)
            ),
            governance=GovernanceEvidence(
                observations=tuple(governance)
            ),
        )
