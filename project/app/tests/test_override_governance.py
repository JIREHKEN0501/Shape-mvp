from project.app.services import tasks


def _patch_override_runtime(
    monkeypatch,
    suppress_overrides,
):
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
                    "task_id": "attention_2",
                    "category": "attention",
                    "difficulty": 2,
                    "instruction": "Attention task",
                    "options": ["A", "B"],
                },
                {
                    "task_id": "attention_3",
                    "category": "attention",
                    "difficulty": 3,
                    "instruction": "Attention task three",
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
            "increase_difficulty": True,
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
            "oscillation_score": 0.0,
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
            "authority_ceiling": 1.0,
            "max_difficulty_shift": None,
            "confidence_cap": None,
            "freeze_category_switching": False,
            "suppress_overrides": suppress_overrides,
            "active_constraints": [],
        },
    )


def test_suppressed_overrides_cannot_change_runtime_difficulty(
    monkeypatch,
):
    """
    Governance suppression must prevent resolved routing overrides
    from changing the runtime difficulty.
    """

    _patch_override_runtime(
        monkeypatch,
        suppress_overrides=True,
    )

    result = tasks.get_next_task_for_participant(
        "override-governance-suppressed"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    difficulty = result["meta"]["difficulty"]
    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["suppress_overrides"] is True

    # Base difficulty is 2 and the routing layer proposes
    # an increase to 3. Governance suppression must prevent
    # that override from changing the runtime difficulty.
    assert difficulty["base"] == 2
    assert difficulty["chosen"] == 2
    assert difficulty["adjustment"] == 0


def test_unsuppressed_overrides_preserve_existing_behavior(
    monkeypatch,
):
    """
    Without governance suppression, the existing routing override
    remains active.
    """

    _patch_override_runtime(
        monkeypatch,
        suppress_overrides=False,
    )

    result = tasks.get_next_task_for_participant(
        "override-governance-active"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    difficulty = result["meta"]["difficulty"]
    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["suppress_overrides"] is False

    # Existing behavior: increase_difficulty changes 2 -> 3.
    assert difficulty["base"] == 2
    assert difficulty["chosen"] == 3
    assert difficulty["adjustment"] == 1
