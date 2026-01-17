from project.app.utils.summary_adapter import build_session_summary


def minimal_completed_cognitive_session():
    return {
        "session_id": "test-session-1",
        "participant_id": "p-123",
        "task_id": "pattern_recognition_v1",
        "session_complete": True,
        "modules": [
            {
                "module_name": "m1",
                "questions": [
                    {
                        "question_id": "q1",
                        "correct": "A",
                        "user_answer": "A",
                        "time_taken_seconds": 3.2,
                    },
                    {
                        "question_id": "q2",
                        "correct": "B",
                        "user_answer": "C",
                        "time_taken_seconds": 6.1,
                    },
                ],
            }
        ],
    }


def minimal_incomplete_session():
    s = minimal_completed_cognitive_session()
    s["session_complete"] = False
    return s


# ----------------------------
# CONTRACT TESTS
# ----------------------------

def test_summary_only_exists_when_complete():
    summary = build_session_summary(minimal_completed_cognitive_session())
    assert summary is not None

    summary = build_session_summary(minimal_incomplete_session())
    assert summary is None


def test_summary_envelope_keys_exist():
    summary = build_session_summary(minimal_completed_cognitive_session())

    assert "summary_version" in summary
    assert "summary_type" in summary
    assert "data" in summary

    assert summary["summary_version"] == "1.0"
    assert summary["summary_type"] == "cognitive"


def test_summary_data_has_expected_keys():
    summary = build_session_summary(minimal_completed_cognitive_session())
    data = summary["data"]

    expected_keys = {
        "total_questions",
        "accuracy_ratio",
        "avg_time_per_question",
        "median_time_per_question",
        "time_variance",
        "speed_accuracy_profile",
    }

    assert expected_keys.issubset(data.keys())


def test_summary_contains_no_identity_fields():
    summary = build_session_summary(minimal_completed_cognitive_session())
    data = summary["data"]

    forbidden = {
        "participant_id",
        "ip",
        "ip_hash",
        "user_agent",
        "events",
        "answers",
    }

    for key in forbidden:
        assert key not in data


def test_accuracy_bounds():
    summary = build_session_summary(minimal_completed_cognitive_session())
    acc = summary["data"]["accuracy_ratio"]

    assert acc is not None
    assert 0.0 <= acc <= 1.0

