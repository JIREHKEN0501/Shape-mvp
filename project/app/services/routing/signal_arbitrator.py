from typing import List, Dict, Any

from .signal_schema import RoutingSignal

from .evidence_builder import EvidenceBuilder
from .evidence_query import EvidenceQuery
from .strategy_policy import evaluate_strategy_policy
from .evidence_authority import evaluate_routing_authority

class SignalArbitrator:
    """
    Resolve competing routing signals into routing directives.

    IMPORTANT:
    Arbitration governs session-level adaptation only.
    It does NOT infer permanent psychological traits.
    """

    def _prepare_signals(
        self,
        signals: List[RoutingSignal]
    ) -> List[RoutingSignal]:
        """
        Prepare routing evidence for arbitration.

        Current responsibility:
            - Pass through all routing signals.

        Future responsibilities:
            - Confidence gating.
            - Evidence eligibility checks.
        """
        return signals

    def _classify_signals(
        self,
        signals: List[RoutingSignal]
    ) -> List[RoutingSignal]:
        """
        Classify routing evidence by evidential role.

        Current responsibility:
            - Pass through all routing signals.

        Future responsibilities:
            - Observation semantics.
            - Interpretation semantics.
            - Prediction semantics.
        """
        return signals

    def resolve(
        self,
        signals: List[RoutingSignal]
    ) -> Dict[str, Any]:

        decisions = {
            "stabilize": False,
            "reduce_difficulty": False,
            "increase_difficulty": False,
            "conflict_detected": False,
            "reasons": []
        }

        prepared_signals = self._prepare_signals(
            signals
        )

        classified_signals = self._classify_signals(
            prepared_signals
        )

        evidence = EvidenceBuilder().build(
            classified_signals
        )

        evidence_query = EvidenceQuery(
            evidence
        )

        # ===================================
        # ROUTING AUTHORITY EVALUATION
        # ===================================

        routing_authority = {}

        for signal in classified_signals:
            metadata = signal.metadata or {}

            routing_authority[signal.signal_type] = (
                evaluate_routing_authority(
                    signal.signal_type,
                    metadata.get("evidence_class"),
                )
            )

        # ===================================
        # STRATEGY POLICY EVALUATION
        # ===================================

        strategy_policy = evaluate_strategy_policy(
            classified_signals
        )

        # Strategy evidence is evaluated for transparency,
        # but does not acquire routing authority here.
        # Any future strategy-derived directive must be
        # explicitly authorized by strategy policy.

        # ===================================
        # FATIGUE-BASED STABILIZATION
        # ===================================

        fatigue = evidence_query.get_temporal(
            "fatigue_risk",
        )
        fatigue_authority = routing_authority.get(
            "fatigue_risk",
            {},
        )

        if (
            fatigue
            and fatigue_authority.get("routing_authorized") is True
            and fatigue_authority.get("authorized_directive")
            == "stabilize"
            and fatigue.value in ["moderate", "elevated"]
        ):
            decisions["stabilize"] = True

            decisions["reasons"].append(
                "Fatigue risk triggered stabilization"
            )

        # ===================================
        # LATENCY-BASED REDUCTION
        # ===================================

        latency = evidence_query.get_temporal(
            "latency_trend",
        )

        latency_authority = routing_authority.get(
            "latency_trend",
            {},
        )

        if (
            latency
            and latency_authority.get("routing_authorized") is True
            and latency_authority.get("authorized_directive")
            == "reduce_difficulty"
            and latency.value == "slowing_down"
        ):
            decisions["reduce_difficulty"] = True

            decisions["reasons"].append(
                "Slowing latency trend detected"
            )

        # ===================================
        # PERFORMANCE-BASED ESCALATION
        # ===================================

        accuracy = evidence_query.get_temporal(
            "accuracy_trend",
        )

        accuracy_authority = routing_authority.get(
            "accuracy_trend",
            {},
        )

        if (
            accuracy
            and accuracy_authority.get("routing_authorized") is True
            and accuracy_authority.get("authorized_directive")
            == "increase_difficulty"
            and accuracy.value == "improving"
        ):
            decisions["increase_difficulty"] = True

            decisions["reasons"].append(
                "Improving accuracy trend detected"
            )

        # ===================================
        # CONFLICT DETECTION
        # ===================================

        if (
            decisions["increase_difficulty"]
            and decisions["reduce_difficulty"]
        ):
            decisions["conflict_detected"] = True

            decisions["reasons"].append(
                "Competing escalation and reduction signals detected"
            )

        decisions["strategy_policy"] = strategy_policy
        decisions["routing_authority"] = routing_authority

        return decisions
