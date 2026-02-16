from project.app.ml.stability.drift_detector import detect_drift


def test_no_drift():
    historical = [0.60, 0.62, 0.59, 0.61]
    current = 0.60

    result = detect_drift(historical, current)

    assert result["drift_detected"] is False
    assert result["confidence"] == "stable"


def test_moderate_drift():
    historical = [0.60, 0.61, 0.59, 0.60]
    current = 0.70  # noticeable jump

    result = detect_drift(historical, current)

    assert result["drift_detected"] is True
    assert result["confidence"] in ["moderate", "strong"]


def test_insufficient_history():
    historical = []
    current = 0.65

    result = detect_drift(historical, current)

    assert result["drift_detected"] is False
    assert result["confidence"] == "insufficient_history"

