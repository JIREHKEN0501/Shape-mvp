from project.app.services.experience_insights import (
    generate_experience_insights,
)


def test_invalid_summary_returns_no_insights():

    result = generate_experience_insights(None)

    assert result["has_insights"] is False
    assert result["message"] == "invalid_summary"


def test_missing_experience_data_returns_no_insights():

    result = generate_experience_insights({
        "experience_id": "experience-1",
        "has_data": False,
        "message": "no_records_for_experience",
    })

    assert result["has_insights"] is False
    assert result["message"] == "no_records_for_experience"


def test_objective_performance_is_reflected():

    result = generate_experience_insights({
        "experience_id": "experience-1",
        "has_data": True,
        "objective_questions": 2,
        "correct_objective_questions": 2,
        "objective_accuracy": 1.0,
        "attempts": [
            {
                "task_id": "pattern_recognition_v1",
                "question_id": "q1",
                "user_answer": "I",
                "correct": "I",
                "time_taken_seconds": 3,
            },
            {
                "task_id": "pattern_recognition_v1",
                "question_id": "q2",
                "user_answer": "30",
                "correct": "30",
                "time_taken_seconds": 4,
            },
        ],
    })

    assert result["has_insights"] is True
    assert len(result["performance"]) == 1
    assert result["performance"][0]["accuracy"] == 1.0
    assert result["performance"][0]["evidence_type"] == "objective"


def test_decision_observations_are_preserved_without_scoring():

    result = generate_experience_insights({
        "experience_id": "experience-1",
        "has_data": True,
        "objective_questions": 0,
        "correct_objective_questions": 0,
        "objective_accuracy": None,
        "attempts": [
            {
                "task_id": "strategy_under_constraint_v1",
                "question_id": "decision_1",
                "user_answer": "gather_information",
                "correct": None,
                "time_taken_seconds": 8,
            },
        ],
    })

    assert len(result["observations"]) == 1

    observation = result["observations"][0]

    assert observation["selected_option"] == (
        "gather_information"
    )

    assert observation["evidence_type"] == (
        "decision_observation"
    )


def test_insights_do_not_assign_stable_personal_traits():

    result = generate_experience_insights({
        "experience_id": "experience-1",
        "has_data": True,
        "objective_questions": 0,
        "correct_objective_questions": 0,
        "objective_accuracy": None,
        "attempts": [],
    })

    assert result["evidence_limits"]

    limits = " ".join(
        result["evidence_limits"]
    ).lower()

    assert "stable personal trait" in limits
    assert "weakness" in limits


def test_next_experiment_is_comparative():

    result = generate_experience_insights({
        "experience_id": "experience-1",
        "has_data": True,
        "objective_questions": 0,
        "correct_objective_questions": 0,
        "objective_accuracy": None,
        "attempts": [],
    })

    assert (
        result["next_experiment"]["type"]
        == "comparable_experience"
    )
