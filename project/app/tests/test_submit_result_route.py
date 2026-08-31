from project.app import create_app


def test_submit_result_scores_and_returns_metrics(monkeypatch):
    app = create_app({"TESTING": True})

    expected_metrics = {
        "task_id": "attention_001",
        "category": "attention",
        "difficulty": 1,
        "submitted_answer": "A",
        "correct_answer": "XABX",
        "is_correct": False,
        "latency_ms": 1200,
        "retries": 1,
        "hesitation": 0,
    }

    monkeypatch.setattr(
        "project.app.routes.submit_result.get_task",
        lambda task_id, include_answer=True: {
            "task_id": "attention_001",
            "category": "attention",
            "difficulty": 1,
            "answer": "XABX",
        },
    )

    monkeypatch.setattr(
        "project.app.routes.submit_result.score_task_attempt",
        lambda **kwargs: expected_metrics,
    )

    with app.test_client() as client:
        response = client.post(
            "/submit_result",
            json={
                "participant_id": "route-test",
                "task_id": "attention_001",
                "answer": "A",
                "latency_ms": 1200,
                "retries": 1,
                "hesitation": 0,
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["metrics"]["task_id"] == "attention_001"
    assert data["metrics"]["is_correct"] is False


def test_submit_result_requires_task_id():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        response = client.post(
            "/submit_result",
            json={
                "participant_id": "route-test",
                "answer": "A",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["ok"] is False
    assert data["error"] == "task_id is required"


def test_submit_result_rejects_unknown_task(monkeypatch):
    app = create_app({"TESTING": True})

    monkeypatch.setattr(
        "project.app.routes.submit_result.get_task",
        lambda task_id, include_answer=True: None,
    )

    with app.test_client() as client:
        response = client.post(
            "/submit_result",
            json={
                "participant_id": "route-test",
                "task_id": "does-not-exist",
                "answer": "A",
            },
        )

    assert response.status_code == 404

    data = response.get_json()

    assert data["ok"] is False
    assert data["error"] == "unknown task_id"
