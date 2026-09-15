from project.app import create_app
from project.app.services.adaptive_authorization import (
    authorize_adaptive_routing,
)
from project.app.services.adaptive_experience import (
    create_authorized_adaptive_experience,
)
from project.app.services.experience_authorization import (
    resolve_adaptive_authorization,
)
from project.app.services.experience_progression_service import (
    load_experience_progression,
)
from project.app.utils.experience_progression import _load_events
from project.app.services.tasks import list_tasks


def _pattern_session():
    return {
        "task_id": "pattern_recognition_v1",
        "modules": [
            {
                "module_name": "pattern_recognition",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "correct": "I",
                        "user_answer": "I",
                        "time_taken_seconds": 3.0,
                    },
                    {
                        "question_id": "pr_q2",
                        "correct": "30",
                        "user_answer": "30",
                        "time_taken_seconds": 3.0,
                    },
                ],
            }
        ],
        "session_complete": True,
    }


def test_authorized_adaptive_experience_executes_real_adaptive_selection():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.test_client() as client:
        # 1. Establish ordinary consent / initial experience.
        consent_response = client.post("/consent")

        assert consent_response.status_code == 200

        participant_cookie = client.get_cookie("participant_id")
        experience_cookie = client.get_cookie("experience_id")

        assert participant_cookie is not None
        assert experience_cookie is not None

        participant_id = participant_cookie.value

        # 2. Explicitly authorize adaptive routing.
        authorization = authorize_adaptive_routing(participant_id)

        assert authorization is True

        # 3. Create an explicitly authorized adaptive experience.
        experience = create_authorized_adaptive_experience(
            participant_id
        )
        assert experience is not None
        assert experience["mode"] == "adaptive"
        assert experience["adaptive_authorized"] is True
        assert experience["authorization_source"] == "consent"

        assert experience["mode"] == "adaptive"
        assert experience["adaptive_authorized"] is True

        experience_id = experience["experience_id"]

        client.set_cookie("experience_id", experience_id)

        # 4. Verify authorization at the execution boundary.
        authorization_check = resolve_adaptive_authorization(
            participant_id=participant_id,
            experience_id=experience_id,
        )

        assert authorization_check["authorized"] is True

        # 5. Complete canonical Task 1.
        response = client.post(
            "/participant/submit_result",
            json=_pattern_session(),
        )

        assert response.status_code == 201

        body = response.get_json()

        assert body["saved"]["task_id"] == "pattern_recognition_v1"

        progression_after_task_1 = load_experience_progression(
            experience_id
        )

        # 6. Call the actual participant-facing next-task route.
        response = client.get(
            f"/tasks/next/{participant_id}"
        )

        assert response.status_code == 200

        body = response.get_json()
        print("NEXT TASK RESPONSE:", body)

        assert body["ok"] is True
        assert body["adaptive_execution"] is True
        assert body["experience_id"] == experience_id

        selected_task = body["task"]

        assert selected_task is not None
        assert selected_task["task_id"]
        assert selected_task["task_id"] != "pattern_recognition_v1"

        # 7. Selected task must come from the adaptive catalog.
        catalog_ids = {
            task["task_id"]
            for task in list_tasks(include_answer=False)
        }

        assert selected_task["task_id"] in catalog_ids

        # Client-facing task must remain sanitized.
        assert "correct" not in selected_task
        assert "decision_code_mapping" not in selected_task

        # 8. Progression must now point to the selected task.
        progression = load_experience_progression(
            experience_id
        )

        assert progression is not None
        assert progression["mode"] == "adaptive"
        assert progression["expected_task"] == selected_task["task_id"]

        # 9. Adaptive transition must have been persisted.
        events = _load_events(experience_id)

        transitions = [
            event
            for event in events
            if event.get("event") == "adaptive_transition"
        ]

        assert transitions

        transition = transitions[-1]

        assert transition["experience_id"] == experience_id
        assert transition["participant_id"] == participant_id
        assert transition["from_task_id"] == "pattern_recognition_v1"
        assert transition["to_task_id"] == selected_task["task_id"]
