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

