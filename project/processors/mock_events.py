import random
import time
from .event_logger import log_event

def make_mock_event(participant_id="user123", task_id="pattern_01", difficulty=1):
    event = {
        "event_type": "task_response",
        "participant_id": participant_id,
        "task_id": task_id,
        "metrics": {
            "response_time_ms": random.randint(500, 3000),
            "accuracy": random.choice([0, 1]),
            "retries": random.randint(0, 2),
            "hint_used": random.choice([True, False]),
            "cursor_idle_ms": random.randint(0, 1000)
        },
        "session_context": {
            "device": "laptop",
            "difficulty_level": difficulty
        },
        "consent_version": "1.0"
    }
    return event

if __name__ == "__main__":
    # generate 10 mock events with a small delay
    for i in range(10):
        e = make_mock_event(participant_id=f"user{i%3}", task_id=f"task_{i%5}", difficulty=(i%3)+1)
        try:
            log_event(e)
        except Exception as exc:
            print("Failed to log:", exc)
        time.sleep(0.15)
