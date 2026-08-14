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

    saved_sessions = []
    completed_experiences = []

    events_file = tmp_path / "experience_events.jsonl"

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

    def fake_save_session(session):
        saved_sessions.append(session)
        return session


    monkeypatch.setattr(
        "project.app.services.experience_progression_service.save_session_result",
        fake_save_session,
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

    assert saved_sessions == []
    assert completed_experiences == []
