#!/usr/bin/env python3
"""
Simple analytics for the sandbox event log (test_data/session_data.json).
Run: python analyze_events.py
"""

import json
import os
from collections import Counter, defaultdict
from statistics import mean

LOG_PATH = os.path.join(os.path.dirname(__file__), "test_data", "session_data.json")

def load_events(path):
    if not os.path.exists(path):
        print("No log file found at", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                print("Log file format unexpected (expected list).")
                return []
            return data
        except Exception as e:
            print("Failed to read log file:", e)
            return []

def summarize(events):
    print("="*40)
    print("Event log summary")
    print("="*40)
    print("Total events:", len(events))

    types = Counter(e.get("event_type", "unknown") for e in events)
    print("\nEvent type counts:")
    for t, c in types.most_common():
        print(f"  {t}: {c}")

    # Task served counts
    served = [e for e in events if e.get("event_type") == "task_served"]
    responses = [e for e in events if e.get("event_type") == "task_response"]

    print(f"\nTask served: {len(served)}")
    print(f"Task responses: {len(responses)}")

    # Top tasks served
    srv_counter = Counter(e.get("task_id") for e in served if e.get("task_id"))
    if srv_counter:
        print("\nTop tasks served:")
        for task, cnt in srv_counter.most_common(10):
            print(f"  {task}: {cnt}")

    # Response accuracy and timing per task
    per_task = defaultdict(list)
    per_participant = defaultdict(list)
    response_times = []

    for r in responses:
        task_id = r.get("task_id", "unknown")
        metrics = r.get("metrics", {})
        accuracy = metrics.get("accuracy")
        rt = metrics.get("response_time_ms")
        # Normalize types
        try:
            accuracy = int(accuracy) if accuracy is not None else None
        except:
            accuracy = None
        try:
            rt = int(rt) if rt is not None else None
        except:
            rt = None

        per_task[task_id].append({"accuracy": accuracy, "rt": rt})
        participant = r.get("participant_id", "anonymous")
        per_participant[participant].append({"accuracy": accuracy, "rt": rt})
        if rt is not None:
            response_times.append(rt)

    print("\nOverall response time stats:")
    if response_times:
        print(f"  Count: {len(response_times)}  Avg (ms): {mean(response_times):.1f}  Min: {min(response_times)}  Max: {max(response_times)}")
    else:
        print("  No response_time_ms values found in logs.")

    print("\nPer-task accuracy (top tasks):")
    for task, recs in sorted(per_task.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        acc_vals = [r["accuracy"] for r in recs if r["accuracy"] is not None]
        rt_vals = [r["rt"] for r in recs if r["rt"] is not None]
        acc_rate = (sum(acc_vals)/len(acc_vals)) if acc_vals else None
        print(f"  {task}: responses={len(recs)}  accuracy_rate={acc_rate:.2f}" if acc_rate is not None else f"  {task}: responses={len(recs)}  accuracy_rate=N/A")
        if rt_vals:
            print(f"    avg_rt_ms={mean(rt_vals):.1f}  min={min(rt_vals)}  max={max(rt_vals)}")

    print("\nPer-participant summary (top participants):")
    for p, recs in sorted(per_participant.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        acc_vals = [r["accuracy"] for r in recs if r["accuracy"] is not None]
        rt_vals = [r["rt"] for r in recs if r["rt"] is not None]
        acc_rate = (sum(acc_vals)/len(acc_vals)) if acc_vals else None
        print(f"  {p}: submissions={len(recs)}  accuracy_rate={acc_rate:.2f}" if acc_rate is not None else f"  {p}: submissions={len(recs)}  accuracy_rate=N/A")
        if rt_vals:
            print(f"    avg_rt_ms={mean(rt_vals):.1f}")

    print("\nDone.")
    print("="*40)

if __name__ == "__main__":
    events = load_events(LOG_PATH)
    summarize(events)
