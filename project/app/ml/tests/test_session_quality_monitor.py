from project.app.ml.quality.session_quality_monitor import evaluate_session_quality


def test_valid_session():
    session = {
        "data": {
            "accuracy_ratio": 0.75,
            "avg_time_per_question": 3.2,
            "total_questions": 10,
        }
    }

    result = evaluate_session_quality(session)

    assert result["quality_status"] == "valid"
    assert result["eligible_for_aggregation"] is True


def test_implausibly_fast():
    session = {
        "data": {
            "accuracy_ratio": 0.8,
            "avg_time_per_question": 0.1,
            "total_questions": 10,
        }
    }

    result = evaluate_session_quality(session)

    assert result["quality_status"] == "flagged"
    assert "implausibly_fast_responses" in result["issues_detected"]


def test_insufficient_engagement():
    session = {
        "data": {
            "accuracy_ratio": 0.9,
            "avg_time_per_question": 2.0,
            "total_questions": 1,
        }
    }

    result = evaluate_session_quality(session)

    assert result["quality_status"] == "flagged"
    assert "insufficient_engagement" in result["issues_detected"]

