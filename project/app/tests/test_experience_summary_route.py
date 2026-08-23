from project.app.routes.participant import participant_bp
from project.app.routes import participant


def _client(monkeypatch):
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(participant_bp)
    return app.test_client()


def test_summary_requires_participant_cookie(monkeypatch):
    client = _client(monkeypatch)

    response = client.get(
        "/participant/experience/experience-1/summary"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "no_participant_cookie"


def test_summary_returns_not_found_for_unknown_experience(
    monkeypatch,
):
    client = _client(monkeypatch)

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: None,
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.get(
        "/participant/experience/experience-1/summary"
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "experience_not_found"


def test_summary_rejects_other_participants_experience(
    monkeypatch,
):
    client = _client(monkeypatch)

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-2",
            "status": "completed",
        },
    )

    called = []

    monkeypatch.setattr(
        participant,
        "generate_experience_summary",
        lambda experience_id: called.append(experience_id),
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.get(
        "/participant/experience/experience-1/summary"
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "unauthorized"

    # Analytics must never be reached for another participant's experience.
    assert called == []


def test_summary_rejects_incomplete_experience(
    monkeypatch,
):
    client = _client(monkeypatch)

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "status": "active",
        },
    )

    called = []

    monkeypatch.setattr(
        participant,
        "generate_experience_summary",
        lambda experience_id: called.append(experience_id),
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.get(
        "/participant/experience/experience-1/summary"
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "experience_not_completed"

    # Analytics must never be reached for an incomplete experience.
    assert called == []


def test_summary_returns_experience_scoped_result(
    monkeypatch,
):
    client = _client(monkeypatch)

    monkeypatch.setattr(
        participant,
        "load_experience_by_id",
        lambda experience_id: {
            "experience_id": experience_id,
            "participant_id": "participant-1",
            "status": "completed",
        },
    )

    expected_summary = {
        "experience_id": "experience-1",
        "has_data": True,
        "total_questions": 4,
        "objective_questions": 3,
        "decision_observations": 1,
        "objective_accuracy": 2 / 3,
        "tasks": {},
        "sessions": {},
        "attempts": [],
    }

    monkeypatch.setattr(
        participant,
        "generate_experience_summary",
        lambda experience_id: expected_summary,
    )

    monkeypatch.setattr(
        participant,
        "audit_record",
        lambda *args, **kwargs: None,
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.get(
        "/participant/experience/experience-1/summary"
    )

    assert response.status_code == 200
    assert response.get_json() == expected_summary
