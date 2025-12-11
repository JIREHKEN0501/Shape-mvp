from project.app import create_app


def _get_client():
    # Create a fresh test app + client each time
    app = create_app({"TESTING": True})
    return app.test_client()


def test_tasks_filter_by_category():
    client = _get_client()
    resp = client.get("/tasks?category=memory_test")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    # we expect at least one memory_test task in your catalog
    assert data["count"] >= 1
    for task in data["tasks"]:
        assert task["category"] == "memory_test"


def test_tasks_filter_by_difficulty():
    client = _get_client()
    resp = client.get("/tasks?difficulty=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["count"] >= 1
    for task in data["tasks"]:
        assert task["difficulty"] == 1


def test_tasks_filter_combined():
    client = _get_client()
    resp = client.get("/tasks?category=attention&difficulty=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    # attention_001 is difficulty 1 in your catalog, so we expect >= 1
    assert data["count"] >= 1
    for task in data["tasks"]:
        assert task["category"] == "attention"
        assert task["difficulty"] == 1

