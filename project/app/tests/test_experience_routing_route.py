from project.app import create_app


def test_experience_routing_requires_participant_cookie():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        response = client.get(
            "/participant/experience/exp_123/routing"
        )

    assert response.status_code == 401
    assert response.get_json()["error"] == "no_participant_cookie"


def test_experience_routing_returns_404_for_missing_experience(monkeypatch):
    app = create_app({"TESTING": True})

    from project.app.routes import participant

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: None,
    )

    with app.test_client() as client:
        client.set_cookie("participant_id", "p_123")

        response = client.get(
            "/participant/experience/exp_missing/routing"
        )

    assert response.status_code == 404
    assert response.get_json()["error"] == "experience_not_found"


def test_experience_routing_rejects_wrong_participant(monkeypatch):
    app = create_app({"TESTING": True})

    from project.app.routes import participant

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "different_participant",
            "status": "completed",
        },
    )

    with app.test_client() as client:
        client.set_cookie("participant_id", "p_123")

        response = client.get(
            "/participant/experience/exp_123/routing"
        )

    assert response.status_code == 403
    assert response.get_json()["error"] == "unauthorized"


def test_experience_routing_rejects_incomplete_experience(monkeypatch):
    app = create_app({"TESTING": True})

    from project.app.routes import participant

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "p_123",
            "status": "active",
        },
    )

    with app.test_client() as client:
        client.set_cookie("participant_id", "p_123")

        response = client.get(
            "/participant/experience/exp_123/routing"
        )

    assert response.status_code == 409
    assert response.get_json()["error"] == "experience_not_completed"


def test_experience_routing_returns_governed_result(monkeypatch):
    app = create_app({"TESTING": True})

    from project.app.routes import participant

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "p_123",
            "status": "completed",
        },
    )

    monkeypatch.setattr(
        participant,
        "evaluate_experience_routing",
        lambda experience_id: {
            "ok": True,
            "experience_id": experience_id,
            "routing": {
                "stabilize": False,
                "reduce_difficulty": False,
                "increase_difficulty": False,
                "conflict_detected": False,
            },
            "trace": {
                "routing_status": "resolved",
                "signals_considered": [],
                "dominant_signals": [],
                "routing_directives": [],
                "conflict_detected": False,
            },
        },
    )

    with app.test_client() as client:
        client.set_cookie("participant_id", "p_123")

        response = client.get(
            "/participant/experience/exp_123/routing"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["experience_id"] == "exp_123"
    assert data["routing"]["conflict_detected"] is False
    assert data["trace"]["routing_status"] == "resolved"
