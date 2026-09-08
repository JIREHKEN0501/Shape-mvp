from flask import Flask

from project.app.routes.participant import participant_bp
from project.app.routes import participant


def _client():
    app = Flask(__name__)
    app.register_blueprint(participant_bp)
    return app.test_client()


def test_consent_rejects_get():
    client = _client()

    response = client.get("/consent")

    assert response.status_code == 405


def test_consent_post_creates_participant_and_experience(
    monkeypatch,
):
    client = _client()

    consent_records = []
    experience_records = []
    experience_events = []

    monkeypatch.setattr(
        participant,
        "append_jsonl_secure",
        lambda path, record: (
            consent_records.append(record)
            if path == participant.CONSENT_LOG
            else experience_records.append(record)
        ),
    )

    monkeypatch.setattr(
        participant,
        "_append_experience_event",
        lambda event: experience_events.append(event),
    )

    monkeypatch.setattr(
        participant,
        "audit_record",
        lambda *args, **kwargs: None,
    )

    response = client.post("/consent")

    assert response.status_code == 200

    body = response.get_json()

    assert body["ok"] is True
    assert body["participant_id"]
    assert body["experience_id"]

    assert len(consent_records) == 1
    assert consent_records[0]["participant_id"] == body["participant_id"]
    assert consent_records[0]["consent_given"] is True
    assert consent_records[0]["consent_version"] == 1

    assert len(experience_records) == 1
    assert experience_records[0]["experience_id"] == body["experience_id"]
    assert experience_records[0]["participant_id"] == body["participant_id"]
    assert experience_records[0]["status"] == "active"

    assert len(experience_events) == 1
    assert experience_events[0]["event"] == "experience_created"
    assert experience_events[0]["experience_id"] == body["experience_id"]

    set_cookies = response.headers.getlist("Set-Cookie")

    assert any(
        "participant_id=" in cookie
        for cookie in set_cookies
    )

    assert any(
        "experience_id=" in cookie
        for cookie in set_cookies
    )

    assert all(
        "HttpOnly" in cookie
        for cookie in set_cookies
        if "participant_id=" in cookie or "experience_id=" in cookie
    )

    assert all(
        "SameSite=Lax" in cookie
        for cookie in set_cookies
        if "participant_id=" in cookie or "experience_id=" in cookie
    )

def test_task_requires_consent():
    client = _client()

    response = client.get(
        "/task/pattern_recognition_v1"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "no_consent"
