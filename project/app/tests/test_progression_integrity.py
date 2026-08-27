from project.app import create_app
import project.app.routes.participant as participant_routes


def make_active_experience():
    return {
        "experience_id": "experience-1",
        "participant_id": "participant-1",
        "status": "active",
        "sequence_version": "1.0",
        "created_ts": "2026-08-13T00:00:00Z",
        "completed_ts": None,
    }


def make_cognitive_session(task_id):
    return {
        "task_id": task_id,
        "modules": [
            {
                "module_name": "test-module",
                "questions": [
                    {
                        "question_id": "q1",
                        "correct": "A",
                        "user_answer": "A",
                        "time_taken_seconds": 3.0,
                    }
                ],
            }
        ],
    }


def test_second_task_is_rejected_before_first_task(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    completed_experiences = []

    events_file = tmp_path / "experience_events.jsonl"

    data_log_file = tmp_path / "data_log.jsonl"

    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG",
        str(data_log_file),
    )

    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG_PATH",
        data_log_file,
    )

    events_file.write_text(
        "\n".join(
            [
                '{"event":"experience_created",'
                '"event_version":"1.0",'
                '"experience_id":"experience-1",'
                '"participant_id":"participant-1",'
                '"sequence_version":"1.0",'
                '"ts":"2026-08-14T12:00:00Z"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        participant_routes,
        "bot_tripwire",
        lambda: None,
    )

    experience_state = make_active_experience()

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience_state,
    )

    monkeypatch.setattr(
        participant_routes,
        "complete_experience",
        lambda experience_id, participant_id: (
            completed_experiences.append(
                (experience_id, participant_id)
            )
        ),
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.post(
            "/participant/submit_result",
            json=make_cognitive_session(
                "strategy_under_constraint_v1"
            ),
        )

    assert response.status_code == 409

    body = response.get_json()

    assert body["error"] == "task_not_expected"

    assert completed_experiences == []

def make_completed_cognitive_session(task_id="pattern_recognition_v1"):
    if task_id == "strategy_under_constraint_v1":
        session = {
            "task_id": task_id,
            "modules": [
                {
                    "module_name": "test-module",
                    "questions": [
                        {
                            "question_id": "q1",
                            "correct": None,
                            "user_answer": "A",
                            "time_taken_seconds": 3.0,
                        }
                    ],
                }
            ],
        }
    else:
        session = make_cognitive_session(task_id)

    session["session_complete"] = True
    return session

def test_duplicate_task_submission_is_rejected(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join([
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}',
            '{"event":"task_completed",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"task_id":"pattern_recognition_v1",'
            '"session_id":"session-1",'
            '"ts":"2026-08-14T12:01:00Z"}',
        ])
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": "pattern_recognition_v1",
            "session_complete": True,
        },
    )

    monkeypatch.setattr(
        participant_routes,
        "bot_tripwire",
        lambda: None,
    )

    experience_state = make_active_experience()

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience_state,
    )

    saved_sessions = []

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: saved_sessions.append(session) or session,
    )

    with app.test_client() as client:
        client.set_cookie("participant_id", "participant-1")
        client.set_cookie("experience_id", "experience-1")

        response = client.post(
            "/participant/submit_result",
            json=make_completed_cognitive_session(
                "pattern_recognition_v1"
            ),
        )

    assert response.status_code == 409
    assert response.get_json()["error"] == "task_not_expected"
    assert saved_sessions == []

def test_submission_after_completed_experience_is_rejected(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    events_file = tmp_path / "experience_events.jsonl"

    events_file.write_text(
        "\n".join([
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}',

            '{"event":"task_completed",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"task_id":"pattern_recognition_v1",'
            '"session_id":"session-1",'
            '"ts":"2026-08-14T12:05:00Z"}',

            '{"event":"task_completed",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"task_id":"strategy_under_constraint_v1",'
            '"session_id":"session-2",'
            '"ts":"2026-08-14T12:08:00Z"}',

            '{"event":"experience_completed",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:10:00Z"}',
        ])
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.load_session_by_id",
        lambda session_id: {
            "session_id": session_id,
            "participant_id": "participant-1",
            "experience_id": "experience-1",
            "task_id": (
                "pattern_recognition_v1"
                if session_id == "session-1"
                else "strategy_under_constraint_v1"
            ),
            "session_complete": True,
        },
    )

    monkeypatch.setattr(
        participant_routes,
        "bot_tripwire",
        lambda: None,
    )

    experience_state = make_active_experience()
    experience_state["status"] = "completed"

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience_state,
    )

    saved_sessions = []

    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        lambda session: saved_sessions.append(session) or session,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.post(
            "/participant/submit_result",
            json=make_completed_cognitive_session(
                "pattern_recognition_v1"
            ),
        )

    assert response.status_code == 409

    payload = response.get_json()

    assert payload["error"] == "experience_not_active"
    assert saved_sessions == []

def test_task_loader_allows_expected_task(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    events_file = tmp_path / "experience_events.jsonl"
    events_file.write_text(
        "\n".join([
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}',
        ]) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    experience = make_active_experience()

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience,
    )

    monkeypatch.setattr(
        participant_routes,
        "load_experience_progression",
        lambda experience_id: {
            "experience_id": "experience-1",
            "participant_id": "participant-1",
            "status": "active",
            "completed_tasks": [],
            "expected_task": "pattern_recognition_v1",
        },
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.get(
            "/task/pattern_recognition_v1"
        )

    assert response.status_code == 200

def test_task_loader_rejects_unexpected_task(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    events_file = tmp_path / "experience_events.jsonl"
    events_file.write_text(
        "\n".join([
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}',
        ]) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    experience = make_active_experience()

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience,
    )

    monkeypatch.setattr(
        participant_routes,
        "load_experience_progression",
        lambda experience_id: {
            "experience_id": "experience-1",
            "participant_id": "participant-1",
            "status": "active",
            "completed_tasks": [],
            "expected_task": "pattern_recognition_v1",
        },
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.get(
            "/task/strategy_under_constraint_v1"
        )

    assert response.status_code == 409

    payload = response.get_json()

    assert payload["error"] == "task_not_expected"
    assert payload["expected_task"] == (
        "pattern_recognition_v1"
    )

def test_task_loader_rejects_completed_experience(
    monkeypatch,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    experience = make_active_experience()
    experience["status"] = "completed"

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.get(
            "/task/pattern_recognition_v1"
        )

    assert response.status_code == 409
    assert response.get_json()["error"] == (
        "experience_not_active"
    )


def test_task_loader_rejects_experience_owned_by_other_participant(
    monkeypatch,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    experience = make_active_experience()
    experience["participant_id"] = "participant-other"

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience,
    )

    with app.test_client() as client:
        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        response = client.get(
            "/task/pattern_recognition_v1"
        )

    assert response.status_code == 403
    assert response.get_json()["error"] == (
        "experience_not_owned"
    )

def test_participant_progression_runs_end_to_end(
    monkeypatch,
    tmp_path,
):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    events_file = tmp_path / "experience_events.jsonl"
    events_file.write_text(
        "\n".join([
            '{"event":"experience_created",'
            '"event_version":"1.0",'
            '"experience_id":"experience-1",'
            '"participant_id":"participant-1",'
            '"sequence_version":"1.0",'
            '"ts":"2026-08-14T12:00:00Z"}',
        ]) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "project.app.utils.experience_progression.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )
    monkeypatch.setattr(
        "project.app.services.experience_progression_service.EXPERIENCE_EVENTS_LOG",
        str(events_file),
    )

    monkeypatch.setattr(
        participant_routes,
        "bot_tripwire",
        lambda: None,
    )

    experience_state = make_active_experience()

    monkeypatch.setattr(
        participant_routes,
        "load_experience_by_id",
        lambda experience_id: experience_state,
    )

    data_log_file = tmp_path / "data_log.jsonl"

    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG",
        str(data_log_file),
    )

    monkeypatch.setattr(
        "project.app.utils.storage.DATA_LOG_PATH",
        data_log_file,
    )

    monkeypatch.setattr(
        "project.app.helpers.DATA_LOG",
        str(data_log_file),
    )

    monkeypatch.setattr(
        "project.app.services.analytics.DATA_LOG",
        str(data_log_file),
    )

    def complete_experience_for_test(
        experience_id,
        participant_id,
    ):
        experience_state["status"] = "completed"
        experience_state["completed_ts"] = (
            "2026-08-14T12:10:00Z"
        )
        return dict(experience_state)

    monkeypatch.setattr(
        participant_routes,
        "complete_experience",
        complete_experience_for_test,
    )

    with app.test_client() as client:

        client.set_cookie(
            "participant_id",
            "participant-1",
        )
        client.set_cookie(
            "experience_id",
            "experience-1",
        )

        # Task 1 must be loadable initially.
        response = client.get(
            "/task/pattern_recognition_v1"
        )
        assert response.status_code == 200

        # Complete Task 1.
        response = client.post(
            "/participant/submit_result",
            json=make_completed_cognitive_session(
                "pattern_recognition_v1"
            ),
        )

        assert response.status_code == 201

        payload = response.get_json()

        assert payload["session_complete"] is True
        assert payload["experience_complete"] is False
        assert payload["next_task_id"] == (
            "strategy_under_constraint_v1"
        )

        # Task 1 must no longer be loadable.
        response = client.get(
            "/task/pattern_recognition_v1"
        )

        assert response.status_code == 409
        assert response.get_json()["error"] == (
            "task_not_expected"
        )

        # Task 2 must now be loadable.
        response = client.get(
            "/task/strategy_under_constraint_v1"
        )

        assert response.status_code == 200

        # Complete Task 2.
        response = client.post(
            "/participant/submit_result",
            json=make_completed_cognitive_session(
                "strategy_under_constraint_v1"
            ),
        )

        assert response.status_code == 201

        payload = response.get_json()

        assert payload["session_complete"] is True
        assert payload["experience_complete"] is True
        assert payload["next_task_id"] is None

        # Completed experience must expose its final summary.
        response = client.get(
            "/participant/experience/experience-1/summary"
        )
        assert response.status_code == 200

        summary_payload = response.get_json()

        assert summary_payload["has_data"] is True
        assert summary_payload["experience_id"] == "experience-1"
        assert summary_payload["total_questions"] == 2
        assert summary_payload["objective_questions"] == 1
        assert summary_payload["decision_observations"] == 1
        assert summary_payload["insights"]["has_insights"] is True

    records = [
        __import__("json").loads(line)
        for line in events_file.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    task_events = [
        event
        for event in records
        if event.get("event") == "task_completed"
    ]

    completion_events = [
        event
        for event in records
        if event.get("event") == "experience_completed"
    ]

    assert [
        event["task_id"]
        for event in task_events
    ] == [
        "pattern_recognition_v1",
        "strategy_under_constraint_v1",
    ]

    assert len(completion_events) == 1
