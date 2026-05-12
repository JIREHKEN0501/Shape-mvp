import random
"""
project/app/services/tasks.py

Central catalog of demo tasks + helpers to fetch them.
Now loads from project/schemas/task_catalog.json instead of a hard-coded dict.

Used by:
- /tasks
- /tasks/<task_id>
- /tasks/next/<participant_id>
- start_session (for task_meta)
- evaluate_task_answer (via get_task)
"""

import json
import os
from typing import Dict, List, Optional, Any

# Path to the JSON catalog
TASK_CATALOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "schemas", "task_catalog.json")
)

# In-memory cache of tasks keyed by task_id
_TASK_CATALOG: Dict[str, Dict[str, Any]] = {}
_CACHE_LOADED: bool = False


# ---------------------------------------------------------------------------
# Adaptive orchestration configuration
# ---------------------------------------------------------------------------

ROUTING_WEIGHTS = {
    "target_category": 4,
    "exact_difficulty": 3,
    "near_difficulty": 1,
    "weakness_bonus_multiplier": 3,

    "precision_bonus": 2,
    "complexity_bonus": 2,
    "stabilization_bonus": 1,
}


STRATEGIES = {
    "precision": {
        "name": "precision_reinforcement",
        "reason": "fast_but_inaccurate",
        "bonus_categories": [
            "attention",
            "logical_reasoning"
        ]
    },

    "complexity": {
        "name": "complexity_escalation",
        "reason": "deliberate_and_accurate",
        "min_difficulty": 2
    },

    "stabilization": {
        "name": "confidence_stabilization",
        "reason": "uncertainty_detected",
        "max_difficulty": 2
    },

    "balanced": {
        "name": "balanced_adaptation",
        "reason": "no_strong_behavior_detected"
    }
}


STRATEGY_KEYS = {
    "precision": STRATEGIES["precision"]["name"],
    "complexity": STRATEGIES["complexity"]["name"],
    "stabilization": STRATEGIES["stabilization"]["name"],
    "balanced": STRATEGIES["balanced"]["name"],
}


def _load_tasks_from_json() -> None:
    """
    Load tasks from the JSON catalog into the in-memory _TASK_CATALOG.

    The JSON file format is:
    {
      "tasks": [
        { "task_id": "...", "category": "...", "difficulty": 1, ... },
        ...
      ]
    }
    """
    global _TASK_CATALOG, _CACHE_LOADED

    if _CACHE_LOADED:
        return

    try:
        with open(TASK_CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = data.get("tasks", [])
        catalog: Dict[str, Dict[str, Any]] = {}
        for task in tasks:
            tid = task.get("task_id")
            if not tid:
                continue
            # Ensure we always have a type for backwards compatibility
            task = dict(task)
            task.setdefault("type", "single_task")
            catalog[tid] = task
        _TASK_CATALOG = catalog
    except Exception:
        # On error, fall back to an empty catalog (endpoint will just return [])
        _TASK_CATALOG = {}

    _CACHE_LOADED = True


def _sanitize_task(task: Dict[str, Any], include_answer: bool = False) -> Dict[str, Any]:
    """Return a copy of the task, optionally hiding the correct answer."""
    data = dict(task)
    if not include_answer and "answer" in data:
        data.pop("answer")
    return data


def list_tasks(include_answer: bool = False) -> List[Dict[str, Any]]:
    """
    Return the full task catalog as a list.
    By default, hides the 'answer' field for safety.
    """
    _load_tasks_from_json()
    tasks = [
        _sanitize_task(task, include_answer=include_answer)
        for task in _TASK_CATALOG.values()
    ]
    # Stable ordering: category -> difficulty -> task_id
    tasks.sort(
        key=lambda t: (
            t.get("category") or "",
            t.get("difficulty") or 0,
            t.get("task_id") or "",
        )
    )
    return tasks


def get_task(task_id: str, include_answer: bool = True) -> Optional[Dict[str, Any]]:
    """
    Return a single task dict by id.
    Returns None if task_id is unknown.
    """
    _load_tasks_from_json()
    task = _TASK_CATALOG.get(task_id)
    if not task:
        return None
    return _sanitize_task(task, include_answer=include_answer)

# ---------------------------------------------------------------------------
# Adaptive next-task engine
# ---------------------------------------------------------------------------

import json
from collections import defaultdict
from pathlib import Path

from project.app.services.routing.signal_extractor import (
    extract_routing_signals
)

from project.app.services.routing.signal_normalizer import (
    normalize_signals
)

from project.app.services.routing.signal_arbitrator import (
    SignalArbitrator
)

from project.app.services.routing.priority_resolver import (
    resolve_signal_priorities
)

from project.app.services.routing.routing_trace import (
    generate_routing_trace
)

from project.app.services.routing.routing_trace_store import (
    persist_routing_trace
)

from project.app.services.routing.orchestration_health import (
    evaluate_orchestration_health
)



def _project_root() -> Path:
    """
    Best-effort helper to find the repository root so we can read logs/data_log.jsonl.

    If anything goes wrong (e.g., file missing), the adaptive engine will
    gracefully fall back to "no history" behaviour.
    """
    # services/ -> app/ -> project/ -> repo root
    return Path(__file__).resolve().parents[3]


def _load_participant_events(participant_id: str) -> List[Dict[str, Any]]:
    """
    Load all logged events for a participant from logs/data_log.jsonl.

    This is intentionally defensive: if the log file doesn't exist or some
    lines are malformed, we just skip them and return what we can.
    """
    events: List[Dict[str, Any]] = []
    log_path = _project_root() / "logs" / "data_log.jsonl"

    if not log_path.exists():
        return events

    try:
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if record.get("participant_id") != participant_id:
                    continue

                events.append(record)
    except OSError:
        # If anything goes wrong, return whatever we accumulated (or empty).
        pass

    return events


def _summarise_history(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a compact view of a participant's history:

    - which tasks have been attempted
    - attempts + correct per category
    - difficulty distribution per category
    """
    attempted_task_ids = set()
    attempts_by_category = defaultdict(int)
    correct_by_category = defaultdict(int)
    difficulties_by_category = defaultdict(list)

    for ev in events:
        # Our submit_result lines usually look like:
        # {
        #   "event_type": "submit_result",
        #   "participant_id": "...",
        #   "task_id": "...",
        #   "metrics": {
        #       "category": "...",
        #       "difficulty": 1,
        #       "is_correct": true,
        #       ...
        #   }
        # }
        metrics = ev.get("metrics", {})
        task_id = ev.get("task_id") or metrics.get("task_id")
        if not task_id:
            continue

        attempted_task_ids.add(task_id)

        category = metrics.get("category")
        difficulty = metrics.get("difficulty")
        is_correct = metrics.get("is_correct")

        if category:
            attempts_by_category[category] += 1
            if isinstance(difficulty, int):
                difficulties_by_category[category].append(difficulty)
            if is_correct is True:
                correct_by_category[category] += 1

    return {
        "attempted_task_ids": attempted_task_ids,
        "attempts_by_category": attempts_by_category,
        "correct_by_category": correct_by_category,
        "difficulties_by_category": difficulties_by_category,
    }


def _build_catalog_index() -> Dict[str, List[Dict[str, Any]]]:
    _load_tasks_from_json()

    by_category: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for task in _TASK_CATALOG.values():  # ✅ CORRECT
        cat = task.get("category")
        if not cat:
            continue
        by_category[cat].append(task)

    return by_category


def _choose_category(summary: Dict[str, Any],
                     by_category: Dict[str, List[Dict[str, Any]]]) -> str:

    attempts_by_category = summary["attempts_by_category"]
    correct_by_category = summary["correct_by_category"]

    # 🧊 Cold start — no history yet
    if not attempts_by_category:
        return random.choice(list(by_category.keys()))

    # --- Compute accuracy per category ---
    category_scores = {}

    for cat in by_category.keys():
        attempts = attempts_by_category.get(cat, 0)
        correct = correct_by_category.get(cat, 0)

        if attempts == 0:
            accuracy = 0.5  # neutral baseline
        else:
            accuracy = correct / attempts

        category_scores[cat] = accuracy

    # --- Build weights (lower accuracy = higher weight) ---
    weights = []

    for cat, acc in category_scores.items():
        weight = 1.0 - acc

        # Bonus for unseen categories
        if attempts_by_category.get(cat, 0) == 0:
            weight += 0.2

        weights.append((cat, weight))

    # --- Weighted random selection ---
    total_weight = sum(w for _, w in weights)

    if total_weight == 0:
        return random.choice(list(by_category.keys()))

    r = random.uniform(0, total_weight)
    upto = 0

    for cat, w in weights:
        if upto + w >= r:
            return cat
        upto += w

    return weights[-1][0]


def _choose_difficulty_for_category(
    category: str,
    summary: Dict[str, Any],
    by_category: Dict[str, List[Dict[str, Any]]],
) -> int:
    """
    Strategy per category:

    - If no history in this category: start at the *lowest* difficulty available.
    - If accuracy > 0.8 and there's a higher difficulty not yet tried much:
        push difficulty up by 1 (challenge).
    - If accuracy < 0.5 and current difficulty > 1:
        step difficulty down by 1 (support).
    - Otherwise, keep current average difficulty (rounded).
    """
    attempts_by_category = summary["attempts_by_category"]
    correct_by_category = summary["correct_by_category"]
    difficulties_by_category = summary["difficulties_by_category"]

    tasks_in_cat = by_category.get(category, [])
    if not tasks_in_cat:
        return 1

    all_difficulties = sorted(
        {int(t.get("difficulty", 1)) for t in tasks_in_cat}
    )
    min_diff = all_difficulties[0]
    max_diff = all_difficulties[-1]

    attempts = attempts_by_category.get(category, 0)
    correct = correct_by_category.get(category, 0)
    diffs = difficulties_by_category.get(category, [])

    # No history -> start at easiest available.
    if attempts == 0 or not diffs:
        return min_diff

    accuracy = correct / attempts if attempts > 0 else 0.5
    avg_diff = round(sum(diffs) / len(diffs))

    # Move difficulty up or down slightly based on accuracy.
    if accuracy > 0.8 and avg_diff < max_diff:
        return avg_diff + 1
    if accuracy < 0.5 and avg_diff > min_diff:
        return avg_diff - 1

    return max(min_diff, min(max_diff, avg_diff))


def _pick_task_for(category: str,
                   difficulty: int,
                   summary: Dict[str, Any],
                   by_category: Dict[str, List[Dict[str, Any]]],
                   prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Choose a specific task:

    1. Prefer tasks in (category, difficulty) that have NOT been attempted yet.
    2. If none, broaden to any difficulty in that category not yet attempted.
    3. If still none, pick any task in the category.
    4. As final fallback, pick any task in the whole catalog.
    """
    attempted = summary["attempted_task_ids"]
    tasks_in_cat = by_category.get(category, [])

    # 1) Same category + difficulty, not attempted.
    candidates = [
        t for t in tasks_in_cat
        if int(t.get("difficulty", 1)) == difficulty
        and t.get("task_id") not in attempted
    ]
    if candidates:
        return random.choice(candidates)

    # 2) Same category, any difficulty, not attempted.
    candidates = [
        t for t in tasks_in_cat
        if t.get("task_id") not in attempted
    ]
    if candidates:
        return random.choice(candidates)
    
    return None

def choose_behavior_strategy(summary: Dict[str, Any]) -> Dict[str, str]:
    """
    Determine adaptive behavioral strategy
    based on observed participant patterns.
    """

    patterns = summary.get("patterns", [])

    for p in patterns:
        text = p.get("pattern", "").lower()

        # ⚡ Fast but inaccurate
        if "fast but inaccurate" in text:
            return STRATEGIES["precision"]

        # 🧠 Deliberate and accurate
        elif "deliberate and accurate" in text:
            return STRATEGIES["complexity"]

        # ❓ Uncertainty / hesitation
        elif "uncertain" in text or "hesitation" in text:
            return STRATEGIES["stabilization"]

    # ✅ Default strategy
    return STRATEGIES["balanced"]


def get_next_task_for_participant(participant_id: str) -> Dict[str, Any]:
    """
    Public API for the adaptive engine.

    Returns a sanitized task dict (no 'answer' field) plus
    a small 'meta' block with how it was chosen.
    """
    # 1) Load participant history from logs.
    events = _load_participant_events(participant_id)
    # Extract previously seen task IDs
    seen_ids = {
        e.get("task_id")
        for e in events
        if e.get("event_type") == "task_attempt" and e.get("task_id")
    }
    summary = _summarise_history(events)

    # 🔮 Pull prediction signals
    prediction = summary.get("behavior_prediction", {})

    # ⏳ Temporal behavioral signals
    temporal = summary.get("temporal_behavior", {})

    fatigue_risk = temporal.get("fatigue_risk")
    latency_trend = temporal.get("latency_trend")
    accuracy_trend = temporal.get("accuracy_trend")
    confidence_trend = temporal.get("confidence_trend")

    # 🧠 Behavioral adaptation strategy
    behavior_strategy = choose_behavior_strategy(summary)

    # =====================================
    # 🧠 Routing orchestration pipeline
    # =====================================

    routing_signals = extract_routing_signals(summary)

    normalized_signals = normalize_signals(
        routing_signals
    )

    arbitrator = SignalArbitrator()

    arbitration_result = arbitrator.resolve(
        normalized_signals
    )

    resolved_routing = resolve_signal_priorities(
        arbitration_result
    )

    routing_trace = generate_routing_trace(
        normalized_signals,
        resolved_routing
    )

    orchestration_health = (
        evaluate_orchestration_health(
            normalized_signals,
            resolved_routing
        )
    )

    persist_routing_trace(
        participant_id,
        routing_trace
    )

    strategy_name = behavior_strategy["name"]
    strategy_reason = behavior_strategy["reason"]

    likely_style = prediction.get("likely_response_style")
    risk = prediction.get("risk_under_time_pressure")
    trend = prediction.get("expected_accuracy_trend")

    # 2) Build an index over the current catalog.
    by_category = _build_catalog_index()

    # 3) Choose category and difficulty.
    chosen_category = _choose_category(summary, by_category)
    base_difficulty = _choose_difficulty_for_category(
        chosen_category, summary, by_category
    )

    chosen_difficulty = base_difficulty
    difficulty_adjustment = 0

    # =====================================
    # 🧠 Behavior-driven strategy adjustment
    # =====================================

    if strategy_name == STRATEGY_KEYS["precision"]:
        # Slow down escalation
        chosen_difficulty = max(base_difficulty - 1, 1)
        difficulty_adjustment = chosen_difficulty - base_difficulty

    elif strategy_name == STRATEGY_KEYS["complexity"]:
        # Encourage deeper challenge
        chosen_difficulty = min(base_difficulty + 1, 3)
        difficulty_adjustment = chosen_difficulty - base_difficulty

    elif strategy_name == STRATEGY_KEYS["stabilization"]:
        # Keep user stable
        chosen_difficulty = min(max(base_difficulty, 1), 2)
        difficulty_adjustment = chosen_difficulty - base_difficulty

    # =====================================
    # ⏳ TEMPORAL-AWARE ADAPTATION
    # =====================================

    # Fatigue stabilization
    if fatigue_risk == "high":
        chosen_difficulty = max(
            chosen_difficulty - 1,
            1
        )
        difficulty_adjustment = (
            chosen_difficulty - base_difficulty
        )

    # Slowing cognition stabilization
    if latency_trend == "slowing_down":
        chosen_difficulty = max(
            chosen_difficulty - 1,
            1
        )
        difficulty_adjustment = (
            chosen_difficulty - base_difficulty
        )

    # Stable/improving trajectory escalation
    if accuracy_trend in ["stable", "improving"]:
        chosen_difficulty = min(
            chosen_difficulty + 1,
            3
        )
        difficulty_adjustment = (
            chosen_difficulty - base_difficulty
        )

    # Confidence instability stabilization
    if confidence_trend == "fluctuating":
        chosen_difficulty = min(
            max(chosen_difficulty, 1),
            2
        )
        difficulty_adjustment = (
            chosen_difficulty - base_difficulty
        )

    # 🧊 Cold start safety
    if not prediction:
        chosen_difficulty = 1
        difficulty_adjustment = chosen_difficulty - base_difficulty

    # =====================================
    # 🧠 Governed orchestration overrides
    # =====================================

    if resolved_routing.get("stabilize"):
        chosen_difficulty = min(
            max(chosen_difficulty, 1),
            2
        )

    if resolved_routing.get("reduce_difficulty"):
        chosen_difficulty = max(
            chosen_difficulty - 1,
            1
        )

    if resolved_routing.get("increase_difficulty"):
        chosen_difficulty = min(
            chosen_difficulty + 1,
            3
        )

    difficulty_adjustment = (
        chosen_difficulty - base_difficulty
    )

    # =========================
    # 🧠 SESSION TASK POOL
    # =========================

    # Build full task pool
    all_tasks = []
    for cat_tasks in by_category.values():
        for t in cat_tasks:
            if t.get("instruction") and t.get("options"):
                all_tasks.append(t)

    # Filter out already seen tasks
    remaining_tasks = [
        t for t in all_tasks
        if t.get("task_id") not in seen_ids
    ]

    # End cleanly if none left
    if not remaining_tasks:
        return {
            "ok": False,
            "message": "Session complete"
        }

    # =====================================
    # 🧠 Adaptive scoring layer
    # =====================================
    def task_score(task):
        score = 0
        reasons = []

        cat = task["category"]
        diff = int(task.get("difficulty", 1))

        # -----------------------------
        # Category targeting priority
        # -----------------------------
        if cat == chosen_category:
            score += ROUTING_WEIGHTS["target_category"]
            reasons.append("Category targeting priority (+4)")

        # -----------------------------
        # Weaker categories get priority
        # -----------------------------
        attempts = summary["attempts_by_category"].get(cat, 0)
        correct = summary["correct_by_category"].get(cat, 0)

        if attempts == 0:
            accuracy = 0.5
        else:
            accuracy = correct / attempts

        weakness_bonus = round(
            (1.0 - accuracy)
            * ROUTING_WEIGHTS["weakness_bonus_multiplier"],
            2
        )
        score += weakness_bonus

        if weakness_bonus > 0:
            reasons.append(
                f"Weak category reinforcement (+{weakness_bonus})"
            )
 
        # -----------------------------
        # Match chosen difficulty
        # -----------------------------
        if diff == chosen_difficulty:
            score += ROUTING_WEIGHTS["exact_difficulty"]
            reasons.append("Exact difficulty match (+3)")

        elif abs(diff - chosen_difficulty) == 1:
            score += ROUTING_WEIGHTS["near_difficulty"]
            reasons.append("Near difficulty match (+1)")

        # -----------------------------
        # Behavior strategy influence
        # -----------------------------
        if strategy_name == STRATEGY_KEYS["precision"]:
            if cat in ["attention", "logical_reasoning"]:
                score += ROUTING_WEIGHTS["precision_bonus"]
                reasons.append(
                    "Precision reinforcement target (+2)"
                )

        elif strategy_name == STRATEGY_KEYS["complexity"]:
            if diff >= 2:
                score += ROUTING_WEIGHTS["complexity_bonus"]
                reasons.append(
                    "Complexity escalation bonus (+2)"
                )

        elif strategy_name == STRATEGY_KEYS["stabilization"]:
            if diff <= 2:
                score += ROUTING_WEIGHTS["stabilization_bonus"]
                reasons.append(
                    "Confidence stabilization bonus (+1)"
                )
              
        task["_selection_score"] =round(score, 2)
        task["_selection_reasons"] = reasons
        return score


    # Rank tasks by adaptive score
    remaining_tasks.sort(key=task_score, reverse=True)

    # Add light randomness to avoid predictability
    top_slice = remaining_tasks[:5] if len(remaining_tasks) >= 5 else remaining_tasks

    raw_task = random.choice(top_slice)

    # 🚨 HARD GUARD — never send broken task to frontend
    if not raw_task.get("instruction") or not raw_task.get("options"):
        print("⚠️ INVALID TASK DETECTED:", raw_task)
        return {
            "ok": False,
            "message": "Invalid task encountered"
        }

    task_payload = _sanitize_task(raw_task, include_answer=False)

    # 🚨 SECOND GUARD (after sanitize, just in case)
    if not task_payload.get("instruction") or not task_payload.get("options"):
        print("⚠️ SANITIZE BROKE TASK:", task_payload)
        return {
            "ok": False,
            "message": "Sanitized task invalid"
        }


    task_payload["meta"] = {
        "strategy": "adaptive_v2",

        "routing": {
            "target_category": chosen_category,
            "selected_category": raw_task.get("category"),

            "selection_score": raw_task.get("_selection_score"),

            "selection_reasons": raw_task.get("_selection_reasons", [])
        },

        "difficulty": {
            "base": base_difficulty,
            "chosen": chosen_difficulty,
            "adjustment": difficulty_adjustment
        },

        "adaptation": {
            "behavior_strategy": strategy_name,
            "strategy_reason": strategy_reason,

            "likely_style": likely_style,
            "risk": risk,
            "trend": trend
        },

        "orchestration": {
            "resolved_routing": resolved_routing,
            "routing_trace": routing_trace,
            "health": orchestration_health
        }
    }
    return task_payload

