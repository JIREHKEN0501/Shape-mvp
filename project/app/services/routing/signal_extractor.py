from typing import List, Dict, Any

from .signal_schema import make_signal


def extract_routing_signals(
    summary: Dict[str, Any]
) -> List:
    """
    Convert behavioral observations into normalized routing signals.

    IMPORTANT:
    Signals describe session-level routing observations only.
    They are NOT permanent psychological traits.
    """

    signals = []

    # -----------------------------------
    # Pull existing HumanOS structures
    # -----------------------------------

    temporal = summary.get("temporal_behavior", {})
    prediction = summary.get("behavior_prediction", {})
    patterns = summary.get("patterns", [])

    # ===================================
    # TEMPORAL SIGNALS
    # ===================================

    fatigue = temporal.get("fatigue_risk")

    if fatigue:
        signals.append(
            make_signal(
                signal_type="fatigue_risk",
                value=fatigue,
                confidence=0.75,
                priority=3,
                source="temporal_behavior",
                metadata={
                    "evidence_class": "interpretation",
                    "dependencies": [
                        "latency_trend",
                        "accuracy_trend",
                        "retry_trend"
                    ],
                    "independent_observations": [
                        "latency_trend",
                        "accuracy_trend",
                        "retry_trend"
                    ]
                }
            )
        )

    latency = temporal.get("latency_trend")

    if latency:
        signals.append(
            make_signal(
                signal_type="latency_trend",
                value=latency,
                confidence=0.65,
                priority=2,
                source="temporal_behavior",
                metadata={
                    "evidence_class": "observation",
                    "dependencies": [],
                    "independent_observations": [
                        "latency_trend"
                    ]
                } 
            )
        )

    confidence_trend = temporal.get("confidence_trend")

    if confidence_trend:
        signals.append(
            make_signal(
                signal_type="confidence_trend",
                value=confidence_trend,
                confidence=0.8,
                priority=3,
                source="temporal_behavior",
                metadata={
                    "evidence_class": "interpretation",
                    "dependencies": [
                        "retry_trend"
                    ],
                    "independent_observations": [
                        "retry_trend"
                    ]
                }
            )
        )

    accuracy_trend = temporal.get("accuracy_trend")

    if accuracy_trend:
        signals.append(
            make_signal(
                signal_type="accuracy_trend",
                value=accuracy_trend,
                confidence=0.7,
                priority=2,
                source="temporal_behavior",
                metadata={
                    "evidence_class": "observation",
                    "dependencies": [],
                    "independent_observations": [
                        "accuracy_trend"
                    ]
                }
            )
        )

    # ===================================
    # BEHAVIOR PREDICTION SIGNALS
    # ===================================

    likely_style = prediction.get("likely_response_style")

    if likely_style:
        signals.append(
            make_signal(
                signal_type="likely_response_style",
                value=likely_style,
                confidence=0.6,
                priority=2,
                source="behavior_prediction",
                metadata={
                    "evidence_class": "prediction",
                    "dependencies": [
                        "category_patterns"
                    ],
                    "independent_observations": [
                        "category_behavior"
                    ]
                }
            )
        )

    risk = prediction.get("risk_under_time_pressure")

    if risk:
        signals.append(
            make_signal(
                signal_type="risk_under_time_pressure",
                value=risk,
                confidence=0.7,
                priority=3,
                source="behavior_prediction",
                metadata={
                    "evidence_class": "prediction",
                    "dependencies": [
                        "category_patterns"
                     ],
                     "independent_observations": [
                         "category_behavior"
                     ]
                }
            )
        )

    # ===================================
    # PATTERN SIGNALS
    # ===================================

    for pattern in patterns:

        pattern_text = pattern.get("pattern")

        if not pattern_text:
            continue

        signals.append(
            make_signal(
                signal_type="behavior_pattern",
                value=pattern_text,
                confidence=0.55,
                priority=1,
                source="pattern_analysis",
                metadata={
                    "evidence_class": "interpretation",
                    "dependencies": [
                        "patterns"
                    ],
                    "independent_observations": []
                }
            )
        )

    return signals
