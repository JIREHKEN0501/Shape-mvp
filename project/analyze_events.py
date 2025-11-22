import json
import time
from pathlib import Path
from typing import Dict, Any, List, Union

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "session_data.json"

if not DATA_PATH.exists():
    DATA_PATH.write_text("[]", encoding="utf-8")


def _read_all() -> List[Dict[str, Any]]:
    """Reads both JSON array or newline-delimited JSON entries."""
    text = DATA_PATH.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
    except Exception:
        pass

    rows = []
    for line in text.splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _write_all(rows: List[Dict[str, Any]]) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def save_session_result(session: Dict[str, Any]) -> Dict[str, Any]:
    """Appends a behavioral or cognitive session to file."""
    rows = _read_all()
    session = dict(session)
    session.setdefault("server_ts", int(time.time() * 1000))
    rows.append(session)
    _write_all(rows)
    return session


# ---------- BEHAVIORAL METRICS ----------

def compute_behavioral_metrics(session: Dict[str, Any]) -> Dict[str, Any]:
    start = session.get("start_ts")
    end = session.get("end_ts")
    events = session.get("events", []) or []

    metrics = {}
    if start and end:
        metrics["total_time_ms"] = max(0, end - start)
    else:
        metrics["total_time_ms"] = None

    hints_used = sum(1 for e in events if e.get("type") == "hint")
    retries = sum(1 for e in events if e.get("type") == "retry")
    keypresses = sum(1 for e in events if e.get("type") == "keypress")

    metrics.update({
        "hints_used": hints_used,
        "retries": retries,
        "keypress_count": keypresses,
    })

    timeline = sorted([e.get("ts") for e in events if isinstance(e.get("ts"), (int, float))])
    hesitation_ms = 0
    threshold = 1500
    for a, b in zip(timeline, timeline[1:]):
        gap = b - a
        if gap > threshold:
            hesitation_ms += gap
    metrics["hesitation_ms"] = hesitation_ms

    score = 100
    if metrics["total_time_ms"]:
        score -= metrics["total_time_ms"] / 1000.0 * 0.5
    score -= metrics["hints_used"] * 5
    score -= metrics["retries"] * 3
    metrics["performance_score"] = round(max(0, score), 2)

    metrics["type"] = "behavioral"
    return metrics


# ---------- COGNITIVE METRICS ----------

def compute_cognitive_metrics(session: Dict[str, Any]) -> Dict[str, Any]:
    """Compute averages across all modules/questions in structured test data."""
    modules = session.get("modules", [])
    if not modules:
        return {"type": "cognitive", "modules": 0, "avg_accuracy": 0, "avg_time": 0}

    total_questions = 0
    correct_count = 0
    total_time = 0.0
    total_hesitation = 0.0
    total_retries = 0

    for module in modules:
        questions = module.get("questions", [])
        for q in questions:
            total_questions += 1
            if q.get("correct"):
                correct_count += 1
            total_time += q.get("time_taken_seconds", 0)
            total_hesitation += q.get("hesitation_seconds", 0)
            total_retries += q.get("retries", 0)

    avg_accuracy = (correct_count / total_questions * 100) if total_questions else 0
    avg_time = (total_time / total_questions) if total_questions else 0
    avg_hesitation = (total_hesitation / total_questions) if total_questions else 0
    avg_retries = (total_retries / total_questions) if total_questions else 0

    return {
        "type": "cognitive",
        "modules": len(modules),
        "questions": total_questions,
        "avg_accuracy": round(avg_accuracy, 2),
        "avg_time_seconds": round(avg_time, 2),
        "avg_hesitation_seconds": round(avg_hesitation, 2),
        "avg_retries": round(avg_retries, 2),
    }


# ---------- MAIN METRIC AGGREGATOR ----------

def aggregate_metrics() -> Dict[str, Any]:
    rows = _read_all()
    if not rows:
        return {"count_total": 0}

    behavioral = []
    cognitive = []

    for s in rows:
        if "events" in s:
            behavioral.append(compute_behavioral_metrics(s))
        elif "modules" in s:
            cognitive.append(compute_cognitive_metrics(s))

    def mean(values):
        return round(sum(values) / len(values), 2) if values else 0

    behavioral_summary = {
        "count": len(behavioral),
        "avg_time_s": mean([m["total_time_ms"] / 1000.0 for m in behavioral if m.get("total_time_ms")]),
        "avg_hints": mean([m["hints_used"] for m in behavioral]),
        "avg_retries": mean([m["retries"] for m in behavioral]),
        "avg_score": mean([m["performance_score"] for m in behavioral]),
    }

    cognitive_summary = {
        "count": len(cognitive),
        "avg_accuracy": mean([m["avg_accuracy"] for m in cognitive]),
        "avg_time_s": mean([m["avg_time_seconds"] for m in cognitive]),
        "avg_hesitation_s": mean([m["avg_hesitation_seconds"] for m in cognitive]),
        "avg_retries": mean([m["avg_retries"] for m in cognitive]),
    }

    return {
        "count_total": len(rows),
        "behavioral_summary": behavioral_summary,
        "cognitive_summary": cognitive_summary,
    }


def export_all() -> List[Dict[str, Any]]:
    return _read_all()


def erase_participant(participant_id: str) -> int:
    rows = _read_all()
    remaining = [r for r in rows if r.get("participant_id") != participant_id]
    removed = len(rows) - len(remaining)
    _write_all(remaining)
    return removed
