from project.app import create_app


def test_legacy_submit_result_route_is_retired():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        response = client.post(
            "/submit_result",
            json={
                "participant_id": "route-test",
                "task_id": "attention_001",
                "answer": "A",
            },
        )

    assert response.status_code == 404
