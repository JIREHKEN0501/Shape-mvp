from project.app.services import tasks


def test_choose_category_returns_available_category_on_cold_start(monkeypatch):
    by_category = {
        "attention": [{"task_id": "a1"}],
        "memory": [{"task_id": "m1"}],
    }

    summary = {
        "attempts_by_category": {},
        "correct_by_category": {},
    }

    monkeypatch.setattr(
        tasks.random,
        "choice",
        lambda values: values[0],
    )

    result = tasks._choose_category(summary, by_category)

    assert result == "attention"


def test_choose_category_favors_lower_accuracy_category(monkeypatch):
    by_category = {
        "strong": [{"task_id": "s1"}],
        "weak": [{"task_id": "w1"}],
    }

    summary = {
        "attempts_by_category": {
            "strong": 10,
            "weak": 10,
        },
        "correct_by_category": {
            "strong": 9,
            "weak": 2,
        },
    }

    captured = {}

    def fake_uniform(start, end):
        captured["weights"] = (start, end)
        return 0.75

    monkeypatch.setattr(
        tasks.random,
        "uniform",
        fake_uniform,
    )

    result = tasks._choose_category(summary, by_category)

    assert result == "weak"
    assert captured["weights"] == (0, 0.9)


def test_choose_category_gives_unseen_category_bonus(monkeypatch):
    by_category = {
        "seen": [{"task_id": "s1"}],
        "unseen": [{"task_id": "u1"}],
    }

    summary = {
        "attempts_by_category": {
            "seen": 10,
            "unseen": 0,
        },
        "correct_by_category": {
            "seen": 5,
            "unseen": 0,
        },
    }

    captured = {}

    def fake_uniform(start, end):
        captured["total_weight"] = end
        return 0.65

    monkeypatch.setattr(
        tasks.random,
        "uniform",
        fake_uniform,
    )

    result = tasks._choose_category(summary, by_category)

    assert result == "unseen"
    assert captured["total_weight"] == 1.2
