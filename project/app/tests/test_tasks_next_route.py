from project.app import create_app
from project.app.routes import get_next_task_for_participant


def test_tasks_next_returns_adaptive_task(monkeypatch):
    app = create_app({"TESTING": True})

    expected_task = {
        "task_id": "task_1",
        "category": "attention",
        "difficulty": 1,
        "instruction": "Choose the correct option.",
        "options": ["A", "B"],
        "meta": {
            "strategy": "adaptive_v2",
        },
    }

    monkeypatch.setattr(
        "project.app.routes.get_next_task_for_participant",
        lambda participant_id: expected_task,
    )

    with app.test_client() as client:
        response = client.get("/tasks/next/test-participant")

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["task"]["task_id"] == "task_1"
    assert data["task"]["instruction"] == "Choose the correct option."
    assert data["task"]["options"] == ["A", "B"]
    assert "answer" not in data["task"]
    assert "correct_answer" not in data["task"]


def test_tasks_next_returns_session_complete(monkeypatch):
    app = create_app({"TESTING": True})

    monkeypatch.setattr(
        "project.app.routes.get_next_task_for_participant",
        lambda participant_id: {
            "ok": False,
            "message": "Session complete",
        },
    )

    with app.test_client() as client:
        response = client.get("/tasks/next/test-participant")

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is False
    assert data["message"] == "Session complete"
    assert "task" not in data


def test_tasks_next_returns_500_on_engine_error(monkeypatch):
    app = create_app({"TESTING": True})

    def raise_error(participant_id):
        raise RuntimeError("engine failure")

    monkeypatch.setattr(
        "project.app.routes.get_next_task_for_participant",
        raise_error,
    )

    with app.test_client() as client:
        response = client.get("/tasks/next/test-participant")

    assert response.status_code == 500

    data = response.get_json()

    assert data["ok"] is False
    assert data["error"] == "internal_error"

def test_task_detail_returns_client_safe_task():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        response = client.get(
            "/tasks/strategy_under_constraint_v1"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    task = data["task"]

    assert task["task_id"] == "strategy_under_constraint_v1"
    assert "decision_code_mapping" not in task

    for module in task["modules"]:
        for question in module["questions"]:
            assert "correct" not in question
