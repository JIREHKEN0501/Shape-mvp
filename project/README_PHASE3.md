# Phase 3 — Sandbox API (quick reference)

Location: `~/shape-mvp/project`

## Key files
- `sandbox_app.py` — FastAPI sandbox with endpoints:
  - `GET /health` — health check
  - `POST /api/log_event` — direct event logging (useful for manual testing)
  - `GET /api/get_task` — fetch a random task (optional query: `category`, `difficulty`, `participant_id`)
  - `POST /api/submit_response` — submit an answer (body: `participant_id`, `task_id`, `answer`, optional `response_time_ms`, `retries`, `hint_used`)
- `schemas/behavioral_schema.json` — validation schema for events
- `schemas/task_catalog.json` — seed tasks
- `processors/event_logger.py` — validation + write-to-`test_data/session_data.json`
- `test_data/session_data.json` — local event store (JSON array)
- `analyze_events.py` — small analytics script (runs locally, no deps)

## Quick start
1. Activate venv:
   ```bash
   cd ~/shape-mvp
   source venv/bin/activate
   cd project
