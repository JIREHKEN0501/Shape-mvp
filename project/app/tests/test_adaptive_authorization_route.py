from flask import Flask

from project.app.routes.participant import participant_bp
from project.app.routes import participant
import os

def _client():
    template_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "templates",
        )
    )

    app = Flask(
        __name__,
        template_folder=template_folder,
    )

    app.register_blueprint(participant_bp)

    return app.test_client()

def test_adaptive_authorization_requires_participant_cookie():
    client = _client()

    response = client.post(
        "/participant/adaptive/authorize"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == (
        "no_participant_cookie"
    )


def test_adaptive_authorization_rejects_failed_authorization(
    monkeypatch,
):
    client = _client()

    monkeypatch.setattr(
        participant,
        "authorize_adaptive_routing",
        lambda participant_id: False,
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.post(
        "/participant/adaptive/authorize"
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == (
        "adaptive_authorization_failed"
    )


def test_adaptive_authorization_fails_if_experience_creation_fails(
    monkeypatch,
):
    client = _client()

    monkeypatch.setattr(
        participant,
        "authorize_adaptive_routing",
        lambda participant_id: True,
    )

    monkeypatch.setattr(
        participant,
        "create_authorized_adaptive_experience",
        lambda participant_id: None,
    )

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.post(
        "/participant/adaptive/authorize"
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == (
        "adaptive_experience_creation_failed"
    )


def test_adaptive_authorization_creates_and_activates_experience(
    monkeypatch,
):
    client = _client()

    created = {
        "experience_id": "adaptive-experience-1",
        "participant_id": "participant-1",
        "mode": "adaptive",
        "adaptive_authorized": True,
        "authorization_source": "consent",
    }

    monkeypatch.setattr(
        participant,
        "authorize_adaptive_routing",
        lambda participant_id: True,
    )

    monkeypatch.setattr(
        participant,
        "create_authorized_adaptive_experience",
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
        "/participant/adaptive/authorize"
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["ok"] is True
    assert body["participant_id"] == "participant-1"
    assert body["experience_id"] == "adaptive-experience-1"
    assert body["mode"] == "adaptive"
    assert body["adaptive_authorized"] is True

    set_cookies = response.headers.getlist("Set-Cookie")

    assert any(
        "experience_id=adaptive-experience-1" in cookie
        for cookie in set_cookies
    )

    assert all(
        "HttpOnly" in cookie
        for cookie in set_cookies
        if "experience_id=" in cookie
    )

    assert all(
        "SameSite=Lax" in cookie
        for cookie in set_cookies
        if "experience_id=" in cookie
    )


def test_adaptive_authorization_page_requires_participant_cookie():
    client = _client()

    response = client.get(
        "/adaptive/authorize"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == (
        "no_participant_cookie"
    )


def test_adaptive_authorization_page_renders_for_participant():
    client = _client()

    client.set_cookie(
        "participant_id",
        "participant-1",
    )

    response = client.get(
        "/adaptive/authorize"
    )

    assert response.status_code == 200
    assert b"Enable an adaptive experience?" in response.data
    assert b"Enable adaptive experience" in response.data

def test_real_adaptive_entry_creates_authorized_experience(
    monkeypatch,
    tmp_path,
):
    from project.app import create_app
    from project.app.utils import logging as logging_utils
    from project.app.utils import experience_lifecycle
    from project.app.utils import experience_progression
    from project.app.services import adaptive_authorization
    import project.app.services.experience_progression_service as progression_service
    import project.app.routes.participant as participant_routes

    consent_log = tmp_path / "consent.jsonl"
    experience_log = tmp_path / "experiences.jsonl"
    experience_events_log = tmp_path / "experience_events.jsonl"

    monkeypatch.setattr(
        logging_utils,
        "CONSENT_LOG",
        str(consent_log),
    )

    monkeypatch.setattr(
        "project.app.utils.consent_loader.CONSENT_LOG",
        str(consent_log),
    )

    monkeypatch.setattr(
        participant_routes,
        "CONSENT_LOG",
        str(consent_log),
    )

    monkeypatch.setattr(
        adaptive_authorization,
        "CONSENT_LOG",
        str(consent_log),
    )

    monkeypatch.setattr(
        experience_lifecycle,
        "EXPERIENCE_LOG",
        str(experience_log),
    )

    monkeypatch.setattr(
        experience_progression,
        "EXPERIENCE_EVENTS_LOG",
        str(experience_events_log),
    )

    monkeypatch.setattr(
        progression_service,
        "EXPERIENCE_EVENTS_LOG",
        str(experience_events_log),
    )
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    with app.test_client() as client:
        # Establish ordinary project consent through the real route.
        consent_response = client.post("/consent")

        assert consent_response.status_code == 200

        participant_id = consent_response.get_json()["participant_id"]

        # The normal consent flow must remain bounded.
        consent_records = consent_log.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        assert len(consent_records) == 1

        import json

        initial_consent = json.loads(consent_records[-1])

        assert initial_consent["participant_id"] == participant_id
        assert initial_consent["consent_given"] is True
        assert initial_consent["adaptive_routing_authorized"] is False

        # Enter the explicit adaptive authorization page.
        page_response = client.get("/adaptive/authorize")

        assert page_response.status_code == 200
        assert b"Enable an adaptive experience?" in page_response.data

        # Explicit participant action authorizes adaptive routing.
        adaptive_response = client.post(
            "/participant/adaptive/authorize"
        )

        assert adaptive_response.status_code == 201

        body = adaptive_response.get_json()

        assert body["ok"] is True
        assert body["participant_id"] == participant_id
        assert body["mode"] == "adaptive"
        assert body["adaptive_authorized"] is True
        assert body["experience_id"]

        adaptive_experience_id = body["experience_id"]

        # Authorization must have been persisted.
        consent_records = consent_log.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        assert len(consent_records) == 2

        authorized_consent = json.loads(consent_records[-1])

        assert authorized_consent["participant_id"] == participant_id
        assert authorized_consent["consent_given"] is True
        assert authorized_consent["adaptive_routing_authorized"] is True

        # The adaptive experience lifecycle record must be persisted
        # with the explicit authorization contract.
        experience_records = experience_log.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        assert len(experience_records) >= 1

        created = json.loads(experience_records[-1])

        assert created["experience_id"] == adaptive_experience_id
        assert created["participant_id"] == participant_id
        assert created["mode"] == "adaptive"
        assert created["adaptive_authorized"] is True
        assert created["authorization_source"] == "consent"

        # The corresponding lifecycle event must also be persisted.
        event_records = experience_events_log.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        assert len(event_records) >= 1

        created_event = json.loads(event_records[-1])

        assert created_event["event"] == "experience_created"
        assert created_event["experience_id"] == adaptive_experience_id
        assert created_event["participant_id"] == participant_id

        # The route must move the participant into the new adaptive
        # experience by replacing the experience cookie.
        cookie_headers = adaptive_response.headers.getlist(
            "Set-Cookie"
        )

        assert any(
            f"experience_id={adaptive_experience_id}" in header
            for header in cookie_headers
        )
