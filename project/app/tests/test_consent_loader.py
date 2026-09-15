from project.app.utils import consent_loader


def test_load_consent_by_participant_returns_latest(
    tmp_path,
    monkeypatch,
):
    log_path = tmp_path / "consent_log.jsonl"

    records = [
        {
            "participant_id": "participant-1",
            "consent_version": 1,
            "consent_given": True,
            "adaptive_routing_authorized": False,
        },
        {
            "participant_id": "participant-2",
            "consent_version": 1,
            "consent_given": True,
            "adaptive_routing_authorized": False,
        },
        {
            "participant_id": "participant-1",
            "consent_version": 2,
            "consent_given": True,
            "adaptive_routing_authorized": True,
        },
    ]

    log_path.write_text(
        "\n".join(
            __import__("json").dumps(record)
            for record in records
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        consent_loader,
        "CONSENT_LOG",
        str(log_path),
    )

    result = consent_loader.load_consent_by_participant(
        "participant-1"
    )

    assert result is not None
    assert result["consent_version"] == 2
    assert result["adaptive_routing_authorized"] is True


def test_load_consent_by_participant_returns_none_when_missing(
    tmp_path,
    monkeypatch,
):
    log_path = tmp_path / "consent_log.jsonl"

    log_path.write_text(
        "",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        consent_loader,
        "CONSENT_LOG",
        str(log_path),
    )

    result = consent_loader.load_consent_by_participant(
        "missing-participant"
    )

    assert result is None


def test_load_consent_by_participant_skips_malformed_records(
    tmp_path,
    monkeypatch,
):
    log_path = tmp_path / "consent_log.jsonl"

    log_path.write_text(
        '{"participant_id": "participant-1", "consent_given": true}\n'
        'not valid json\n'
        '{"participant_id": "participant-2", "consent_given": true}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        consent_loader,
        "CONSENT_LOG",
        str(log_path),
    )

    result = consent_loader.load_consent_by_participant(
        "participant-1"
    )

    assert result is not None
    assert result["consent_given"] is True
