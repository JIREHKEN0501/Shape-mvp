from project.app.services import tasks


def test_pick_task_prefers_unattempted_matching_difficulty(monkeypatch):
    by_category = {
        "attention": [
            {
                "task_id": "task_1",
                "category": "attention",
                "difficulty": 1,
            },
            {
                "task_id": "task_2",
                "category": "attention",
                "difficulty": 2,
            },
            {
                "task_id": "task_3",
                "category": "attention",
                "difficulty": 2,
            },
        ]
    }

    summary = {
        "attempted_task_ids": {"task_1"},
    }

    monkeypatch.setattr(
        tasks.random,
        "choice",
        lambda candidates: candidates[0],
    )

    result = tasks._pick_task_for(
        "attention",
        2,
        summary,
        by_category,
        {},
    )

    assert result["task_id"] == "task_2"


def test_pick_task_falls_back_to_unattempted_different_difficulty(monkeypatch):
    by_category = {
        "attention": [
            {
                "task_id": "task_1",
                "category": "attention",
                "difficulty": 1,
            },
            {
                "task_id": "task_2",
                "category": "attention",
                "difficulty": 2,
            },
        ]
    }

    summary = {
        "attempted_task_ids": {"task_2"},
    }

    monkeypatch.setattr(
        tasks.random,
        "choice",
        lambda candidates: candidates[0],
    )

    result = tasks._pick_task_for(
        "attention",
        2,
        summary,
        by_category,
        {},
    )

    assert result["task_id"] == "task_1"


def test_pick_task_returns_none_when_category_is_exhausted():
    by_category = {
        "attention": [
            {
                "task_id": "task_1",
                "category": "attention",
                "difficulty": 1,
            },
            {
                "task_id": "task_2",
                "category": "attention",
                "difficulty": 2,
            },
        ]
    }

    summary = {
        "attempted_task_ids": {"task_1", "task_2"},
    }

    result = tasks._pick_task_for(
        "attention",
        1,
        summary,
        by_category,
        {},
    )

    assert result is None
