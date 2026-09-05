from typing import Any, Dict

from project.app.services.analytics import generate_experience_summary

from .routing_trace import generate_routing_trace
from .signal_arbitrator import SignalArbitrator
from .signal_extractor import extract_routing_signals
from .signal_normalizer import normalize_signals


def evaluate_experience_routing(
    experience_id: str,
) -> Dict[str, Any]:
    """
    Evaluate governed routing evidence produced by one experience.

    The evaluation is strictly scoped to the supplied experience_id.
    It does not select or mutate the participant's next task.

    Strategy decisions may contribute evidence and transparency
    information, but do not acquire routing authority unless an
    explicit strategy policy authorizes a directive.
    """

    if not experience_id:
        return {
            "ok": False,
            "experience_id": experience_id,
            "error": "experience_id_required",
        }

    summary = generate_experience_summary(experience_id)

    if not summary.get("has_data"):
        return {
            "ok": False,
            "experience_id": experience_id,
            "error": summary.get(
                "message",
                "experience_summary_unavailable",
            ),
        }

    signals = extract_routing_signals(summary)
    normalized_signals = normalize_signals(signals)

    arbitration_result = SignalArbitrator().resolve(
        normalized_signals
    )

    routing_trace = generate_routing_trace(
        normalized_signals,
        arbitration_result,
    )

    return {
        "ok": True,
        "experience_id": experience_id,
        "routing": arbitration_result,
        "trace": routing_trace,
    }
