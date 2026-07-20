from typing import List, Dict, Any

from .signal_schema import RoutingSignal

from .evidence_builder import EvidenceBuilder


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

    def _build_signal_map(
        self,
        signals: List[RoutingSignal]
    ) -> Dict[str, RoutingSignal]:
        """
        Organize routing signals for arbitration.
        """

        signal_map = {}

        for signal in signals:
            signal_map[signal.signal_type] = signal

        return signal_map

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

        signal_map = self._build_signal_map(
            classified_signals
        )

        # ===================================
        # FATIGUE-BASED STABILIZATION
        # ===================================

        fatigue = signal_map.get("fatigue_risk")

        if fatigue and fatigue.value in ["moderate", "elevated"]:
            decisions["stabilize"] = True

            decisions["reasons"].append(
                "Fatigue risk triggered stabilization"
            )

        # ===================================
        # LATENCY-BASED REDUCTION
        # ===================================

        latency = signal_map.get("latency_trend")

        if latency and latency.value == "slowing_down":
            decisions["reduce_difficulty"] = True

            decisions["reasons"].append(
                "Slowing latency trend detected"
            )

        # ===================================
        # PERFORMANCE-BASED ESCALATION
        # ===================================

        accuracy = signal_map.get("accuracy_trend")

        if accuracy and accuracy.value == "improving":
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

        return decisions
