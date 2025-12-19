#!/bin/bash
set -e

echo "🟦 Starting Participant Session..."
curl -s -X POST http://localhost:5000/start_session \
    -H "Content-Type: application/json" \
    -d '{"source":"pilot_test"}' | jq

echo "🟩 Pulling Next Task..."
curl -s http://localhost:5000/tasks/next/pilot_test_user | jq

echo "🟧 Submitting Result..."
curl -s -X POST http://localhost:5000/submit_result \
    -H "Content-Type: application/json" \
    -d '{
        "participant_id": "pilot_test_user",
        "task_id": "pattern_001",
        "answer": "32"
    }' | jq

echo "🟪 Fetching Summary..."
curl -s http://localhost:5000/metrics/summary/pilot_test_user | jq

echo "Pilot test completed."

