from project.app import create_app

def test_tasks_next_requires_experience_context():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "test-participant",
        )

        response = client.get(
            "/tasks/next/test-participant"
        )

    assert response.status_code == 409

    data = response.get_json()

    assert data["ok"] is False
    assert data["error"] == "experience_context_required"

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

def test_tasks_next_uses_adaptive_execution_for_authorized_experience(
    monkeypatch,
):
    app = create_app({"TESTING": True})

    monkeypatch.setattr(
        "project.app.routes.load_experience_progression",
        lambda experience_id: {
            "status": "active",
            "participant_id": "test-participant",
            "mode": "adaptive",
            "adaptive_authorized": True,
            "completed_tasks": [
                "pattern_recognition_v1",
            ],
            "expected_task": None,
            "sequence_version": "1.0",
        },
    )

    captured = {}

    def fake_adaptive_execution(
        participant_id,
        experience_id,
        from_task_id,
    ):
        captured["participant_id"] = participant_id
        captured["experience_id"] = experience_id
        captured["from_task_id"] = from_task_id

        return {
            "ok": True,
            "experience_id": experience_id,
            "from_task_id": from_task_id,
            "next_task_id": "adaptive_task_001",
            "task": {
                "task_id": "adaptive_task_001",
                "instruction": "Adaptive task",
                "options": ["A", "B"],
            },
        }

    monkeypatch.setattr(
        "project.app.routes.execute_next_adaptive_task",
        fake_adaptive_execution,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "test-participant",
        )
        client.set_cookie(
            "experience_id",
            "experience-adaptive",
        )

        response = client.get(
            "/tasks/next/test-participant"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["task"]["task_id"] == "adaptive_task_001"
    assert data["experience_id"] == "experience-adaptive"

    assert captured == {
        "participant_id": "test-participant",
        "experience_id": "experience-adaptive",
        "from_task_id": "pattern_recognition_v1",
    }

def test_tasks_next_bounded_experience_does_not_execute_adaptive(
    monkeypatch,
):
    app = create_app({"TESTING": True})

    monkeypatch.setattr(
        "project.app.routes.load_experience_progression",
        lambda experience_id: {
            "status": "active",
            "participant_id": "test-participant",
            "mode": "bounded",
            "adaptive_authorized": False,
            "completed_tasks": [
                "pattern_recognition_v1",
                "strategy_under_constraint_v1",
            ],
            "expected_task": None,
            "sequence_version": "1.0",
        },
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "Adaptive execution must not run for bounded experiences"
        )

    monkeypatch.setattr(
        "project.app.routes.execute_next_adaptive_task",
        fail_if_called,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "test-participant",
        )
        client.set_cookie(
            "experience_id",
            "experience-bounded",
        )

        response = client.get(
            "/tasks/next/test-participant"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is False
    assert data["message"] == "Session complete"
    assert data["experience_complete"] is True

def test_tasks_next_real_adaptive_execution_persists_transition(
    monkeypatch,
):
    from project.app.services import adaptive_experience_execution
    from project.app.services import experience_authorization

    app = create_app({"TESTING": True})

    participant_id = "adaptive-participant"
    experience_id = "adaptive-experience"

    consent = {
        "participant_id": participant_id,
        "consent_given": True,
        "adaptive_routing_authorized": True,
    }

    experience = {
        "experience_id": experience_id,
        "participant_id": participant_id,
        "mode": "adaptive",
        "adaptive_authorized": True,
        "mode_version": "1.0",
        "authorization_source": "consent",
    }

    monkeypatch.setattr(
        experience_authorization,
        "load_consent_by_participant",
        lambda participant: consent
        if participant == participant_id
        else None,
    )

    monkeypatch.setattr(
        experience_authorization,
        "load_experience_by_id",
        lambda exp_id: experience
        if exp_id == experience_id
        else None,
    )

    monkeypatch.setattr(
        experience_authorization,
        "experience_belongs_to_participant",
        lambda exp, participant: (
            exp["participant_id"] == participant
        ),
    )

    monkeypatch.setattr(
        experience_authorization,
        "resolve_experience_mode",
        lambda exp: {
            "mode": "adaptive",
            "adaptive_authorized": True,
            "mode_version": "1.0",
            "authorization_source": "consent",
        },
    )

    monkeypatch.setattr(
        "project.app.routes.load_experience_progression",
        lambda exp_id: {
            "status": "active",
            "participant_id": participant_id,
            "mode": "adaptive",
            "adaptive_authorized": True,
            "completed_tasks": [
                "pattern_recognition_v1",
            ],
            "expected_task": None,
            "sequence_version": "1.0",
        },
    )

    monkeypatch.setattr(
        adaptive_experience_execution,
        "get_next_task_for_participant",
        lambda participant, experience_id=None: {
            "ok": True,
            "task_id": "adaptive_task_001",
            "instruction": "Adaptive task",
            "options": ["A", "B"],
        },
    )

    monkeypatch.setattr(
        adaptive_experience_execution,
        "resolve_adaptive_task_eligibility",
        lambda exp_id, task_id: {
            "eligible": True,
            "reason": "adaptive_task_eligible",
            "experience_id": exp_id,
            "candidate_task_id": task_id,
        },
    )

    captured_transition = {}

    def fake_transition(
        experience_id,
        participant_id,
        from_task_id,
        to_task_id,
    ):
        captured_transition.update({
            "experience_id": experience_id,
            "participant_id": participant_id,
            "from_task_id": from_task_id,
            "to_task_id": to_task_id,
        })
        return {
            "ok": True,
            "event": {
                "event": "adaptive_transition",
                "from_task_id": from_task_id,
                "to_task_id": to_task_id,
            },
        }

    monkeypatch.setattr(
        adaptive_experience_execution,
        "execute_adaptive_transition",
        fake_transition,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            participant_id,
        )
        client.set_cookie(
            "experience_id",
            experience_id,
        )

        response = client.get(
            f"/tasks/next/{participant_id}"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["task"]["task_id"] == "adaptive_task_001"
    assert data["experience_id"] == experience_id
    assert data["adaptive_execution"] is True

    assert captured_transition == {
        "experience_id": experience_id,
        "participant_id": participant_id,
        "from_task_id": "pattern_recognition_v1",
        "to_task_id": "adaptive_task_001",
    }
