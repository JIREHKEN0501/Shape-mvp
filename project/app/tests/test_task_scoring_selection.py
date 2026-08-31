from project.app.services import tasks


def test_adaptive_selection_randomizes_only_within_top_five(monkeypatch):
    participant_id = "scoring-selection-test"

    catalog = [
        {
            "task_id": "task_1",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task one",
            "options": ["A", "B"],
        },
        {
            "task_id": "task_2",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task two",
            "options": ["A", "B"],
        },
        {
            "task_id": "task_3",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task three",
            "options": ["A", "B"],
        },
        {
            "task_id": "task_4",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task four",
            "options": ["A", "B"],
        },
        {
            "task_id": "task_5",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task five",
            "options": ["A", "B"],
        },
        {
            "task_id": "task_6",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Task six",
            "options": ["A", "B"],
        },
    ]

    monkeypatch.setattr(
        tasks,
        "_load_participant_events",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "_build_catalog_index",
        lambda: {"attention": catalog},
    )

    monkeypatch.setattr(
        tasks,
        "generate_participant_summary",
        lambda participant_id: {
            "patterns": [],
            "behavior_prediction": {},
            "temporal_behavior": {},
        },
    )

    monkeypatch.setattr(tasks, "extract_routing_signals", lambda summary: [])
    monkeypatch.setattr(tasks, "normalize_signals", lambda signals: [])

    monkeypatch.setattr(
        tasks.SignalArbitrator,
        "resolve",
        lambda self, signals: {
            "stabilize": False,
            "reduce_difficulty": False,
            "increase_difficulty": False,
            "conflict_detected": False,
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_signal_priorities",
        lambda result: result,
    )

    monkeypatch.setattr(
        tasks,
        "generate_routing_trace",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "evaluate_orchestration_health",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "load_recent_orchestration_history",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "detect_orchestration_oscillation",
        lambda history: {"oscillation_score": 0.0},
    )

    monkeypatch.setattr(
        tasks,
        "persist_routing_trace",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        tasks,
        "_choose_category",
        lambda summary, by_category: "attention",
    )

    monkeypatch.setattr(
        tasks,
        "_choose_difficulty_for_category",
        lambda category, summary, by_category: 1,
    )

    captured = {}

    def fake_choice(candidates):
        captured["candidates"] = candidates
        return candidates[0]

    monkeypatch.setattr(tasks.random, "choice", fake_choice)

    result = tasks.get_next_task_for_participant(participant_id)

    assert result["task_id"] == "task_1"

    candidate_ids = [
        item["task"]["task_id"]
        for item in captured["candidates"]
    ]

    assert len(candidate_ids) == 5
    assert candidate_ids == [
        "task_1",
        "task_2",
        "task_3",
        "task_4",
        "task_5",
    ]
    assert "task_6" not in candidate_ids
