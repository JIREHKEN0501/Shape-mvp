import json

from project.app import create_app
from project.app.routes import participant
from project.app.services.routing import routing_trace_store
from project.app.services import experience_progression_service
from project.app.utils import logging as logging_utils


def _write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def test_erase_anonymizes_all_participant_linked_logs(
    monkeypatch,
    tmp_path,
):
    app = create_app({"TESTING": True})

    participant_id = "participant-erase-123"
    replacement = f"anonymized:{__import__('hashlib').sha256(
        participant_id.encode()
    ).hexdigest()[:16]}"

    audit_log = tmp_path / "audit.jsonl"
    consent_log = tmp_path / "consent.jsonl"
    data_log = tmp_path / "data.jsonl"
    experience_log = tmp_path / "experience.jsonl"
    experience_events_log = tmp_path / "experience_events.jsonl"
    routing_log = tmp_path / "routing_trace.jsonl"

    records = [
        {"participant_id": participant_id, "value": "audit"},
    ]
    _write_jsonl(audit_log, records)
    _write_jsonl(consent_log, records)
    _write_jsonl(data_log, records)
    _write_jsonl(experience_log, records)
    _write_jsonl(experience_events_log, records)
    _write_jsonl(routing_log, records)

    monkeypatch.setattr(
        logging_utils,
        "AUDIT_LOG",
        str(audit_log),
    )
    monkeypatch.setattr(
        logging_utils,
        "CONSENT_LOG",
        str(consent_log),
    )
    monkeypatch.setattr(
        logging_utils,
        "DATA_LOG",
        str(data_log),
    )
    monkeypatch.setattr(
        logging_utils,
        "EXPERIENCE_LOG",
        str(experience_log),
    )
    monkeypatch.setattr(
        experience_progression_service,
        "EXPERIENCE_EVENTS_LOG",
        str(experience_events_log),
    )
    monkeypatch.setattr(
        routing_trace_store,
        "_trace_log_path",
        lambda: routing_log,
    )
    monkeypatch.setattr(
        participant,
        "audit_record",
        lambda *args, **kwargs: None,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            participant_id,
        )

        response = client.post("/erase")

    assert response.status_code == 200

    data = response.get_json()

    assert data["ok"] is True
    assert data["replacement"] == replacement

    for path in (
        audit_log,
        consent_log,
        data_log,
        experience_log,
        experience_events_log,
        routing_log,
    ):
        contents = path.read_text(encoding="utf-8")
        assert participant_id not in contents
        assert replacement in contents


def test_erase_requires_participant_cookie():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        response = client.post("/erase")

    assert response.status_code == 400

    data = response.get_json()

    assert data["ok"] is False
    assert data["error"] == "no_participant_cookie"
