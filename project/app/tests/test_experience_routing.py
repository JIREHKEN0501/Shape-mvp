from project.app.services.routing.experience_routing import (
    evaluate_experience_routing,
)


def test_experience_routing_is_scoped_to_requested_experience(
    monkeypatch,
):
    summaries = {
        "experience-A": {
            "experience_id": "experience-A",
            "has_data": True,
            "strategy": {
                "decisions": [
                    {
                        "question_id": "suc_q1",
                        "selected_option": "Invest in long-term payoff",
                        "decision_code": "long_term_payoff",
                    }
                ]
            },
        },
        "experience-B": {
            "experience_id": "experience-B",
            "has_data": True,
            "strategy": {
                "decisions": [
                    {
                        "question_id": "suc_q1",
                        "selected_option": "Secure immediate stability",
                        "decision_code": "stability_first",
                    }
                ]
            },
        },
    }

    captured = {}

    def fake_summary(experience_id):
        captured["experience_id"] = experience_id
        return summaries[experience_id]

    monkeypatch.setattr(
        "project.app.services.routing.experience_routing.generate_experience_summary",
        fake_summary,
    )

    result = evaluate_experience_routing("experience-B")

    assert result["ok"] is True
    assert result["experience_id"] == "experience-B"
    assert captured["experience_id"] == "experience-B"

    strategy_observations = result["routing"]["strategy_policy"][
        "strategy_observations"
    ]

    assert len(strategy_observations) == 1
    assert (
        strategy_observations[0]["decision_code"]
        == "stability_first"
    )


def test_strategy_remains_evidence_only_in_experience_routing(
    monkeypatch,
):
    summary = {
        "experience_id": "experience-1",
        "has_data": True,
        "strategy": {
            "decisions": [
                {
                    "question_id": "suc_q1",
                    "selected_option": "Invest in long-term payoff",
                    "decision_code": "long_term_payoff",
                }
            ]
        },
    }

    monkeypatch.setattr(
        "project.app.services.routing.experience_routing.generate_experience_summary",
        lambda experience_id: summary,
    )

    result = evaluate_experience_routing("experience-1")

    assert result["ok"] is True

    strategy_policy = result["routing"]["strategy_policy"]

    assert strategy_policy["routing_authorized"] is False
    assert strategy_policy["authorized_directives"] == []

    strategy_authority = result["routing"]["routing_authority"].get(
        "strategy_decision"
    )

    assert strategy_authority is not None
    assert strategy_authority["routing_authorized"] is False
    assert strategy_authority["authorized_directive"] is None


def test_experience_routing_returns_transparent_trace(
    monkeypatch,
):
    summary = {
        "experience_id": "experience-1",
        "has_data": True,
        "strategy": {
            "decisions": [
                {
                    "question_id": "suc_q1",
                    "selected_option": "Gather more information before acting",
                    "decision_code": "information_first",
                }
            ]
        },
    }

    monkeypatch.setattr(
        "project.app.services.routing.experience_routing.generate_experience_summary",
        lambda experience_id: summary,
    )

    result = evaluate_experience_routing("experience-1")

    assert result["ok"] is True

    trace = result["trace"]

    assert trace["routing_status"] == "resolved"
    assert trace["strategy_policy"]["routing_authorized"] is False
    assert len(trace["signals_considered"]) == 1
    assert (
        trace["signals_considered"][0]["signal_type"]
        == "strategy_decision"
    )


def test_experience_routing_fails_closed_without_experience_id():
    result = evaluate_experience_routing("")

    assert result == {
        "ok": False,
        "experience_id": "",
        "error": "experience_id_required",
    }


def test_experience_routing_propagates_missing_summary(
    monkeypatch,
):
    monkeypatch.setattr(
        "project.app.services.routing.experience_routing.generate_experience_summary",
        lambda experience_id: {
            "experience_id": experience_id,
            "has_data": False,
            "message": "no_records_for_experience",
        },
    )

    result = evaluate_experience_routing("experience-missing")

    assert result == {
        "ok": False,
        "experience_id": "experience-missing",
        "error": "no_records_for_experience",
    }
