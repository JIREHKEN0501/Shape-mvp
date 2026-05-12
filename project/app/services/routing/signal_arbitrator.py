from typing import List, Dict, Any

from .signal_schema import RoutingSignal


class SignalArbitrator:
    """
    Resolve competing routing signals into routing directives.

    IMPORTANT:
    Arbitration governs session-level adaptation only.
    It does NOT infer permanent psychological traits.
    """

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

        signal_map = {}

        # -----------------------------------
        # Build lookup map
        # -----------------------------------

        for signal in signals:
            signal_map[signal.signal_type] = signal.value

        # ===================================
        # FATIGUE-BASED STABILIZATION
        # ===================================

        fatigue = signal_map.get("fatigue_risk")

        if fatigue in ["moderate", "elevated"]:
            decisions["stabilize"] = True

            decisions["reasons"].append(
                "Fatigue risk triggered stabilization"
            )

        # ===================================
        # LATENCY-BASED REDUCTION
        # ===================================

        latency = signal_map.get("latency_trend")

        if latency == "slowing_down":
            decisions["reduce_difficulty"] = True

            decisions["reasons"].append(
                "Slowing latency trend detected"
            )

        # ===================================
        # PERFORMANCE-BASED ESCALATION
        # ===================================

        accuracy = signal_map.get("accuracy_trend")

        if accuracy == "improving":
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
