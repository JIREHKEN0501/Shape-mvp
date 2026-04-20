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
    """
    Strategy:
    1. Prefer categories with *fewest attempts* (coverage).
    2. Among those, prioritise the category with *lowest accuracy*
       (focus on weaker area).
    3. If no history at all, just pick the first category in the catalog.
    """
    attempts_by_category = summary["attempts_by_category"]
    correct_by_category = summary["correct_by_category"]

    # No history yet -> just take the first category present in catalog.
    if not attempts_by_category:
        return next(iter(by_category.keys()))

    # Step 1: categories with the smallest number of attempts.
    min_attempts = min(attempts_by_category.values()) if attempts_by_category else 0
    candidate_cats = [
        cat for cat, n in attempts_by_category.items() if n == min_attempts
    ]

    # There might be categories that have *zero* attempts and aren't in the dict yet.
    for cat in by_category.keys():
        if cat not in attempts_by_category:
            candidate_cats.append(cat)

    # Deduplicate while preserving order a bit.
    seen = set()
    unique_candidates = []
    for cat in candidate_cats:
        if cat not in seen:
            unique_candidates.append(cat)
            seen.add(cat)

    # Step 2: among candidates, choose the one with the lowest accuracy.
    best_cat = None
    best_accuracy = 1.1  # higher than any possible accuracy

    for cat in unique_candidates:
        attempts = attempts_by_category.get(cat, 0)
        correct = correct_by_category.get(cat, 0)
        if attempts == 0:
            accuracy = 0.5  # neutral starting assumption
        else:
            accuracy = correct / attempts

        if accuracy < best_accuracy:
            best_accuracy = accuracy
            best_cat = cat

    # Fallback (shouldn't happen, but let's be safe)
    if not best_cat:
        best_cat = next(iter(by_category.keys()))

    return best_cat


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
                   by_category: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
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
        if int(t.get("difficulty", 1)) == difficulty and t.get("task_id") not in attempted
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

    # 3) Any task in the category.
    if tasks_in_cat:
        return tasks_in_cat[0]

    # 4) Last resort: any task in the catalog.
    return next(iter(_TASK_CATALOG.values()))


def get_next_task_for_participant(participant_id: str) -> Dict[str, Any]:
    """
    Public API for the adaptive engine.

    Returns a sanitized task dict (no 'answer' field) plus
    a small 'meta' block with how it was chosen.
    """
    # 1) Load participant history from logs.
    events = _load_participant_events(participant_id)
    summary = _summarise_history(events)

    # 2) Build an index over the current catalog.
    by_category = _build_catalog_index()

    # 3) Choose category and difficulty.
    chosen_category = _choose_category(summary, by_category)
    chosen_difficulty = _choose_difficulty_for_category(
        chosen_category, summary, by_category
    )

    # 4) Pick a concrete task.
    raw_task = _pick_task_for(chosen_category, chosen_difficulty, summary, by_category)

    task_payload = _sanitize_task(raw_task, include_answer=False)
    task_payload["meta"] = {
        "strategy": "adaptive_v1",
        "chosen_category": chosen_category,
        "chosen_difficulty": chosen_difficulty,
    }
    return task_payload

