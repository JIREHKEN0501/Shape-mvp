from project.app.services import tasks


def _patch_category_runtime(monkeypatch, freeze_category_switching):
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
                    "task_id": "attention_1",
                    "category": "attention",
                    "difficulty": 2,
                    "instruction": "Attention task",
                    "options": ["A", "B"],
                }
            ],
            "logical_reasoning": [
                {
                    "task_id": "logic_1",
                    "category": "logical_reasoning",
                    "difficulty": 2,
                    "instruction": "Logic task",
                    "options": ["A", "B"],
                }
            ],
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
            "constraints": {
                "freeze_category_switching":
                    freeze_category_switching
            },
        },
    )

    monkeypatch.setattr(
        tasks,
        "resolve_governance_constraints",
        lambda governance_state: {
            "authority_ceiling": 1.0,
            "max_difficulty_shift": None,
            "confidence_cap": None,
            "freeze_category_switching":
                freeze_category_switching,
            "suppress_overrides": False,
            "active_constraints": [],
        },
    )


def test_category_switching_is_frozen_by_governance(monkeypatch):
    _patch_category_runtime(
        monkeypatch,
        freeze_category_switching=True,
    )

    result = tasks.get_next_task_for_participant(
        "category-governance-frozen"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    assert result["category"] == "attention"

    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["freeze_category_switching"] is True

    routing = result["meta"]["routing"]

    assert routing["target_category"] == "attention"
    assert routing["selected_category"] == "attention"


def test_category_switching_remains_available_without_governance(
    monkeypatch,
):
    _patch_category_runtime(
        monkeypatch,
        freeze_category_switching=False,
    )

    result = tasks.get_next_task_for_participant(
        "category-governance-open"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["freeze_category_switching"] is False
