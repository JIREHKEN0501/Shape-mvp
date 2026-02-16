from project.app.ml.aggregation.task_difficulty_aggregator import aggregate_sessions


def test_quality_filtering_excludes_bad_sessions():
    sessions = [
        {
            "task_id": "t1",
            "data": {
                "accuracy_ratio": 0.8,
                "avg_time_per_question": 2.0,
                "time_variance": 0.5,
                "total_questions": 10,
            },
        },
        {
            # Bad session (too fast)
            "task_id": "t1",
            "data": {
                "accuracy_ratio": 0.9,
                "avg_time_per_question": 0.1,
                "time_variance": 0.1,
                "total_questions": 10,
            },
        },
    ]

    task_lookup = {
        "t1": {
            "declared_difficulty": 0.5,
            "domain": "education",
            "structure_version": "1.0",
        }
    }

    aggregated_list = aggregate_sessions(sessions, task_lookup)
    aggregated = aggregated_list[0]["aggregated_metrics"]

    assert aggregated["num_sessions"] == 1
    assert aggregated["filtered_sessions"] == 1
