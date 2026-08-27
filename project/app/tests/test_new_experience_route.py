from flask import Flask

from project.app.routes.participant import participant_bp
from project.app.routes import participant


def _client():
    app = Flask(__name__)
    app.register_blueprint(participant_bp)
    return app.test_client()


def test_new_experience_requires_participant_cookie(
    monkeypatch,
):
    client = _client()

    response = client.post(
        "/participant/experience/new"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == (
        "no_participant_cookie"
    )


def test_new_experience_creates_new_experience_for_existing_participant(
    monkeypatch,
):
    client = _client()

    created = {
        "experience_id": "experience-2",
        "participant_id": "participant-1",
        "status": "active",
        "sequence_version": "1.0",
        "created_ts": "2026-08-26T10:00:00",
        "completed_ts": None,
    }

    monkeypatch.setattr(
        participant,
        "create_experience",
        lambda participant_id: created,
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

    response = client.post(
        "/participant/experience/new"
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["ok"] is True
    assert body["participant_id"] == "participant-1"
    assert body["experience_id"] == "experience-2"
    assert body["next_task_id"] == (
        "pattern_recognition_v1"
    )

    assert "experience_id=experience-2" in (
        response.headers.get("Set-Cookie", "")
    )
