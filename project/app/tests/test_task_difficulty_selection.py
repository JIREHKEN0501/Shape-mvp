from project.app.services.tasks import _choose_difficulty_for_category


def test_no_history_starts_at_lowest_available_difficulty():
    summary = {
        "attempts_by_category": {},
        "correct_by_category": {},
        "difficulties_by_category": {},
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 1


def test_high_accuracy_increases_difficulty():
    summary = {
        "attempts_by_category": {
            "attention": 10,
        },
        "correct_by_category": {
            "attention": 9,
        },
        "difficulties_by_category": {
            "attention": [1, 1, 1, 1],
        },
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 2


def test_low_accuracy_decreases_difficulty():
    summary = {
        "attempts_by_category": {
            "attention": 10,
        },
        "correct_by_category": {
            "attention": 4,
        },
        "difficulties_by_category": {
            "attention": [3, 3, 3, 3],
        },
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 2


def test_stable_accuracy_keeps_average_difficulty():
    summary = {
        "attempts_by_category": {
            "attention": 10,
        },
        "correct_by_category": {
            "attention": 6,
        },
        "difficulties_by_category": {
            "attention": [1, 2, 2, 3],
        },
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 2


def test_high_accuracy_at_max_difficulty_does_not_exceed_catalog():
    summary = {
        "attempts_by_category": {
            "attention": 10,
        },
        "correct_by_category": {
            "attention": 10,
        },
        "difficulties_by_category": {
            "attention": [3, 3, 3],
        },
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 3


def test_low_accuracy_at_min_difficulty_does_not_go_below_catalog():
    summary = {
        "attempts_by_category": {
            "attention": 10,
        },
        "correct_by_category": {
            "attention": 0,
        },
        "difficulties_by_category": {
            "attention": [1, 1, 1],
        },
    }

    by_category = {
        "attention": [
            {"task_id": "task_1", "difficulty": 1},
            {"task_id": "task_2", "difficulty": 2},
            {"task_id": "task_3", "difficulty": 3},
        ]
    }

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 1


def test_empty_category_falls_back_to_difficulty_one():
    summary = {
        "attempts_by_category": {},
        "correct_by_category": {},
        "difficulties_by_category": {},
    }

    by_category = {}

    result = _choose_difficulty_for_category(
        "attention",
        summary,
        by_category,
    )

    assert result == 1
