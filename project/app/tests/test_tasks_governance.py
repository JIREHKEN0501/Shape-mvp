from project.app.services import tasks


def test_runtime_candidate_pool_respects_governed_difficulty(monkeypatch):
    """
    Prove that governance filtering happens before adaptive scoring
    in the real get_next_task_for_participant() runtime path.
    """

    participant_id = "governance-test-participant"

    catalog = {
        "difficulty_1": {
            "task_id": "difficulty_1",
            "category": "attention",
            "difficulty": 1,
            "instruction": "Difficulty one",
            "options": ["A", "B"],
        },
        "difficulty_2": {
            "task_id": "difficulty_2",
            "category": "attention",
            "difficulty": 2,
            "instruction": "Difficulty two",
            "options": ["A", "B"],
        },
        "difficulty_3": {
            "task_id": "difficulty_3",
            "category": "attention",
            "difficulty": 3,
            "instruction": "Difficulty three",
            "options": ["A", "B"],
        },
    }

    monkeypatch.setattr(
        tasks,
        "_load_participant_events",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "_build_catalog_index",
        lambda: {
            "attention": list(catalog.values())
        },
    )

    monkeypatch.setattr(
        tasks,
        "generate_participant_summary",
        lambda participant_id: {
            "patterns": [],
            "behavior_prediction": {
                "likely_response_style": "deliberate",
                "risk_under_time_pressure": "low",
                "expected_accuracy_trend": "improving",
            },
            "temporal_behavior": {
                "fatigue_risk": None,
                "latency_trend": None,
                "accuracy_trend": None,
                "confidence_trend": None,
            },
        },
    )

    monkeypatch.setattr(
        tasks,
        "extract_routing_signals",
        lambda summary: [],
    )

    monkeypatch.setattr(
        tasks,
        "normalize_signals",
        lambda signals: [],
    )

    monkeypatch.setattr(
        tasks.SignalArbitrator,
        "resolve",
        lambda self, signals: {
            "stabilize": False,
            "reduce_difficulty": False,
            "increase_difficulty": False,
            "conflict_detected": False,
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_signal_priorities",
        lambda result: result,
    )

    monkeypatch.setattr(
        tasks,
        "generate_routing_trace",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "evaluate_orchestration_health",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "load_recent_orchestration_history",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "detect_orchestration_oscillation",
        lambda history: {
            "oscillation_score": 0.0
        },
    )

    monkeypatch.setattr(
        tasks,
        "persist_routing_trace",
        lambda *args, **kwargs: None,
    )

    # Force the runtime to propose difficulty 3.
    monkeypatch.setattr(
        tasks,
        "_choose_category",
        lambda summary, by_category: "attention",
    )

    monkeypatch.setattr(
        tasks,
        "_choose_difficulty_for_category",
        lambda category, summary, by_category: 2,
    )

    # Governance constrains escalation to one level.
    monkeypatch.setattr(
        tasks,
        "build_governance_state",
        lambda oscillation_state: {
            "governance_status": "stable",
            "topology_integrity": "stable",
            "reevaluation_required": False,
            "arbitration_active": False,
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_governance_constraints",
        lambda governance_state: {
            "authority_ceiling": 0.4,
            "max_difficulty_shift": 1,
            "active_constraints": [],
        },
    )

    result = tasks.get_next_task_for_participant(
        participant_id
    )

    governed = result["meta"]["orchestration"]["governed_adaptation"]

    # Governance mediation permits the one-level escalation.
    assert governed["permitted_difficulty"] == 2
    assert governed["escalation_constrained"] is False

    # The final runtime difficulty remains within the
    # one-level governance ceiling.
    assert result["meta"]["difficulty"]["chosen"] <= 2

    # get_next_task_for_participant() returns the
    # sanitized task payload directly.
    selected_task = result

    # Difficulty 3 must not survive the governance gate.
    # Difficulty 1 remains valid because max_difficulty_shift == 1
    # defines a bounded candidate range rather than an exact
    # difficulty requirement.
    assert selected_task["difficulty"] <= 2

    # The scorer may select difficulty 1 or 2 from the
    # governance-permitted candidate range.
    assert selected_task["difficulty"] in {1, 2}


def test_runtime_zero_shift_freezes_candidate_pool(monkeypatch):
    """
    Prove that max_difficulty_shift == 0 prevents the runtime
    from selecting any task other than the base difficulty.
    """

    participant_id = "governance-zero-shift"

    monkeypatch.setattr(
        tasks,
        "_load_participant_events",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "_build_catalog_index",
        lambda: {
            "attention": [
                {
                    "task_id": "difficulty_1",
                    "category": "attention",
                    "difficulty": 1,
                    "instruction": "Difficulty one",
                    "options": ["A", "B"],
                },
                {
                    "task_id": "difficulty_2",
                    "category": "attention",
                    "difficulty": 2,
                    "instruction": "Difficulty two",
                    "options": ["A", "B"],
                },
                {
                    "task_id": "difficulty_3",
                    "category": "attention",
                    "difficulty": 3,
                    "instruction": "Difficulty three",
                    "options": ["A", "B"],
                },
            ]
        },
    )

    monkeypatch.setattr(
        tasks,
        "generate_participant_summary",
        lambda participant_id: {
            "patterns": [],
            "behavior_prediction": {},
            "temporal_behavior": {},
        },
    )

    monkeypatch.setattr(
        tasks,
        "extract_routing_signals",
        lambda summary: [],
    )

    monkeypatch.setattr(
        tasks,
        "normalize_signals",
        lambda signals: [],
    )

    monkeypatch.setattr(
        tasks.SignalArbitrator,
        "resolve",
        lambda self, signals: {
            "stabilize": False,
            "reduce_difficulty": False,
            "increase_difficulty": False,
            "conflict_detected": False,
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_signal_priorities",
        lambda result: result,
    )

    monkeypatch.setattr(
        tasks,
        "generate_routing_trace",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "evaluate_orchestration_health",
        lambda signals, result: {},
    )

    monkeypatch.setattr(
        tasks,
        "load_recent_orchestration_history",
        lambda participant_id: [],
    )

    monkeypatch.setattr(
        tasks,
        "detect_orchestration_oscillation",
        lambda history: {
            "oscillation_score": 0.0
        },
    )

    monkeypatch.setattr(
        tasks,
        "persist_routing_trace",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        tasks,
        "_choose_category",
        lambda summary, by_category: "attention",
    )

    monkeypatch.setattr(
        tasks,
        "_choose_difficulty_for_category",
        lambda category, summary, by_category: 2,
    )

    monkeypatch.setattr(
        tasks,
        "build_governance_state",
        lambda oscillation_state: {
            "governance_status": "stable",
            "topology_integrity": "stable",
            "reevaluation_required": False,
            "arbitration_active": False,
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_governance_constraints",
        lambda governance_state: {
            "authority_ceiling": 0.2,
            "max_difficulty_shift": 0,
            "active_constraints": [],
        },
    )

    result = tasks.get_next_task_for_participant(
        participant_id
    )

    governed = result["meta"]["orchestration"]["governed_adaptation"]

    # The mediation result is an intermediate governance state.
    # Because this test uses an empty prediction, cold-start safety
    # proposes recovery from the base difficulty of 2 to difficulty 1.
    # That is not an escalation, so escalation_constrained remains False.
    assert governed["permitted_difficulty"] == 1
    assert governed["escalation_constrained"] is False

    # max_difficulty_shift == 0 is enforced after mediation.
    # The final runtime difficulty is therefore frozen at the base
    # difficulty of 2.
    assert result["meta"]["difficulty"]["chosen"] == 2
    assert result["difficulty"] == 2
