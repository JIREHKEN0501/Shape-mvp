from typing import Any, Dict, Iterable, List

from .signal_schema import RoutingSignal, make_signal


def calibration_result_to_signal(
    calibration_result: Dict[str, Any],
    experience_task_ids: Iterable[str],
) -> RoutingSignal | None:
    """
    Convert one externally supplied task-level calibration result into
    a routing signal scoped to the supplied experience.

    Calibration is population/task-level evidence. This adapter does not
    calculate calibration, select calibration snapshots, personalize
    calibration, or grant routing authority.
    """

    if not isinstance(calibration_result, dict):
        return None

    task_id = calibration_result.get("task_id")
    if not task_id:
        return None

    allowed_task_ids = set(experience_task_ids)

    if task_id not in allowed_task_ids:
        return None

    try:
        confidence = float(calibration_result.get("confidence", 0.0))
    except (TypeError, ValueError):
        return None

    if not 0.0 <= confidence <= 1.0:
        return None

    return make_signal(
        signal_type="task_calibration",
        value=dict(calibration_result),
        confidence=confidence,
        priority=1,
        source="task_calibration",
        metadata={
            "evidence_class": "calibration",
            "task_id": task_id,
        },
    )


def calibration_results_to_signals(
    calibration_results: Iterable[Dict[str, Any]],
    experience_task_ids: Iterable[str],
) -> List[RoutingSignal]:
    """
    Convert valid calibration results into experience-scoped signals.

    Invalid or out-of-scope calibration results are ignored safely.
    """

    signals: List[RoutingSignal] = []

    for result in calibration_results:
        signal = calibration_result_to_signal(
            result,
            experience_task_ids,
        )
        if signal is not None:
            signals.append(signal)

    return signals
