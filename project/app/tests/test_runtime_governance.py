from project.app.services import tasks


def _patch_runtime(monkeypatch, max_shift):
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
            "max_difficulty_shift": max_shift,
            "active_constraints": [],
        },
    )


def test_runtime_governance_metadata_matches_selected_task(monkeypatch):
    """
    Prove that the runtime's returned task, difficulty metadata,
    resolved governance constraints, and governed adaptation
    remain internally consistent.
    """

    _patch_runtime(monkeypatch, max_shift=1)

    result = tasks.get_next_task_for_participant(
        "runtime-governance-consistency"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    selected_task = result

    difficulty = result["meta"]["difficulty"]

    orchestration = result["meta"]["orchestration"]

    governed = orchestration["governed_adaptation"]

    constraints = orchestration["resolved_constraints"]

    assert constraints["max_difficulty_shift"] == 1

    assert governed["permitted_difficulty"] == 2

    assert difficulty["base"] == 2

    assert difficulty["chosen"] == 2

    assert difficulty["adjustment"] == 0

    # Governance must prevent candidates above the final
    # permitted difficulty, while allowing lower eligible
    # candidates to remain available for scoring.
    assert selected_task["difficulty"] <= (
        governed["permitted_difficulty"]
    )



def test_runtime_governance_blocks_difficulty_above_permitted_range(
    monkeypatch,
):
    """
    Prove that an upstream difficulty proposal above the governance
    ceiling cannot survive into the candidate pool or returned task.
    """

    _patch_runtime(monkeypatch, max_shift=1)

    # Force an upstream proposal beyond the canonical range.
    monkeypatch.setattr(
        tasks,
        "_choose_difficulty_for_category",
        lambda category, summary, by_category: 3,
    )

    # The improving trajectory will attempt another escalation,
    # potentially producing a proposal above the permitted runtime
    # boundary. Governance must still cap the final result.
    result = tasks.get_next_task_for_participant(
        "runtime-governance-ceiling"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    selected_task = result

    difficulty = result["meta"]["difficulty"]

    governed = (
        result["meta"]["orchestration"]
        ["governed_adaptation"]
    )

    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["max_difficulty_shift"] == 1

    assert 1 <= governed["permitted_difficulty"] <= 3

    assert difficulty["chosen"] <= 3

    assert selected_task["difficulty"] <= 3

    assert (
        selected_task["difficulty"]
        <= governed["permitted_difficulty"]
    )


def test_zero_shift_governance_freezes_runtime_task(
    monkeypatch,
):
    """
    Prove that zero-shift governance freezes candidate selection
    at the base difficulty.
    """

    _patch_runtime(monkeypatch, max_shift=0)

    result = tasks.get_next_task_for_participant(
        "runtime-governance-zero-shift"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    selected_task = result

    difficulty = result["meta"]["difficulty"]

    governed = (
        result["meta"]["orchestration"]
        ["governed_adaptation"]
    )

    constraints = (
        result["meta"]["orchestration"]
        ["resolved_constraints"]
    )

    assert constraints["max_difficulty_shift"] == 0

    assert difficulty["base"] == 2

    assert difficulty["chosen"] == 2

    assert selected_task["difficulty"] == 2

    assert governed["permitted_difficulty"] == 2

def test_runtime_persists_complete_governance_audit_trace(monkeypatch):
    """
    Prove that the final persisted routing trace contains the complete
    governance audit structure produced after governance mediation.
    """
    _patch_runtime(monkeypatch, max_shift=1)

    persisted = []

    def capture_persisted_trace(
        participant_id,
        trace,
        health=None,
    ):
        persisted.append({
            "participant_id": participant_id,
            "trace": trace,
            "health": health,
        })

    monkeypatch.setattr(
        tasks,
        "persist_routing_trace",
        capture_persisted_trace,
    )

    result = tasks.get_next_task_for_participant(
        "runtime-governance-audit"
    )

    assert isinstance(result, dict)
    assert result.get("task_id") is not None

    # Exactly one final audit trace should be persisted.
    assert len(persisted) == 1

    persisted_trace = persisted[0]["trace"]

    assert "governance" in persisted_trace

    governance = persisted_trace["governance"]

    assert "state" in governance
    assert "resolved_constraints" in governance
    assert "selection_trace" in governance
    assert "confidence" in governance
    assert "governed_adaptation" in governance

    # The persisted governance state must match the runtime result.
    runtime_governance = (
        result["meta"]["orchestration"]
    )

    assert (
        governance["state"]
        == runtime_governance["governance_state"]
    )

    assert (
        governance["resolved_constraints"]
        == runtime_governance["resolved_constraints"]
    )

    assert (
        governance["selection_trace"]
        == runtime_governance["selection_trace"]
    )

    assert (
        governance["confidence"]
        == runtime_governance["confidence"]
    )

    # The persisted adaptation must represent the final
    # governance-mediated difficulty decision.
    assert (
        governance["governed_adaptation"]
        == runtime_governance["governed_adaptation"]
    )
