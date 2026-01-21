import pytest
from project.app.utils.summary_adapter import build_session_summary


def valid_cognitive_session():
    return {
        "session_complete": True,
        "task_id": "pattern_recognition_v1",
        "modules": [
            {
                "module_name": "m1",
                "questions": [
                    {
                        "question_id": "q1",
                        "correct": "A",
                        "user_answer": "A",
                        "time_taken_seconds": 3.0,
                    }
                ],
            }
        ],
    }


def test_valid_summary_passes():
    summary = build_session_summary(valid_cognitive_session())
    assert summary["summary_version"] == "1.0"
    assert summary["summary_type"] == "cognitive"
    assert "data" in summary

