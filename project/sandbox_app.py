from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from processors.event_logger import log_event

# Create FastAPI instance
app = FastAPI(title="Cognitive Behavioral Sandbox API")

# Define the expected data structure for incoming requests
class EventPayload(BaseModel):
    event_type: str
    participant_id: str
    task_id: str
    timestamp: str | None = None
    metrics: Dict[str, Any]
    session_context: Dict[str, Any] | None = None
    consent_version: str | None = None

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/log_event")
async def api_log_event(payload: EventPayload):
    """
    Receives a behavioral event from the frontend or external test client.
    Validates the JSON schema using event_logger and appends the event to session_data.json.
    """
    event = payload.dict()
    try:
        log_event(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "status": "stored",
        "task_id": event.get("task_id"),
        "participant": event.get("participant_id")
    }


import json
import random
from fastapi import Query

@app.get("/api/get_task")
def get_task(category: str | None = Query(None), difficulty: int | None = Query(None)):
    """
    Returns a random task from schemas/task_catalog.json filtered by optional
    category and difficulty query parameters.
    """
    catalog_path = "schemas/task_catalog.json"
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f).get("tasks", [])
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Task catalog not found at {catalog_path}")

    filtered = data
    if category:
        filtered = [t for t in filtered if t.get("category") == category]
    if difficulty is not None:
        filtered = [t for t in filtered if t.get("difficulty") == difficulty]

    if not filtered:
        raise HTTPException(status_code=404, detail="No matching task found")

    return random.choice(filtered)


from fastapi import Body

@app.post("/api/submit_response")
def submit_response(payload: dict = Body(...)):
    """
    Receives a submitted task response, compares it to the catalog,
    calculates accuracy, and logs a task_response event.
    """
    task_id = payload.get("task_id")
    participant_id = payload.get("participant_id", "anonymous")
    answer = payload.get("answer")

    # --- Load task catalog ---
    with open("schemas/task_catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)["tasks"]

    task = next((t for t in catalog if t["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # --- Evaluate response ---
    is_correct = str(answer).strip().lower() == str(task["answer"]).strip().lower()

    # --- Log event ---
    event = {
        "event_type": "task_response",
        "participant_id": participant_id,
        "task_id": task_id,
        "timestamp": None,  # logger will fill
        "metrics": {
            "response_time_ms": int(payload.get("response_time_ms", 0)),
            "accuracy": 1 if is_correct else 0,
            "retries": int(payload.get("retries", 0)),
            "hint_used": bool(payload.get("hint_used", False))
        },
        "session_context": {
            "category": task["category"],
            "difficulty": task["difficulty"]
        },
        "consent_version": "1.0"
    }
    log_event(event)

    return {
        "task_id": task_id,
        "participant_id": participant_id,
        "correct": is_correct
    }
