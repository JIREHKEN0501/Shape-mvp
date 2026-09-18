#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-127.0.0.1:5000}"

COOKIE_JAR="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_JAR"
}

trap cleanup EXIT

echo "🟦 Starting duplicate-task negative-path test..."

echo "🟨 Giving consent..."

CONSENT_RESPONSE=$(curl -sS \
    -c "$COOKIE_JAR" \
    -X POST "http://$BASE_URL/consent" \
    -H "Content-Type: application/json")

echo "$CONSENT_RESPONSE" | jq

echo "$CONSENT_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$CONSENT_RESPONSE" | jq -e '.participant_id != null' >/dev/null
echo "$CONSENT_RESPONSE" | jq -e '.experience_id != null' >/dev/null

PARTICIPANT_ID=$(echo "$CONSENT_RESPONSE" | jq -r '.participant_id')
EXPERIENCE_ID=$(echo "$CONSENT_RESPONSE" | jq -r '.experience_id')

echo "🟩 Participant created: $PARTICIPANT_ID"
echo "🟩 Bounded experience created: $EXPERIENCE_ID"

echo "🟨 Completing canonical Task 1..."

TASK1_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "pattern_recognition_v1",
        "modules": [
            {
                "module_name": "pilot",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "user_answer": "I",
                        "time_taken_seconds": 3.0
                    },
                    {
                        "question_id": "pr_q2",
                        "user_answer": "30",
                        "time_taken_seconds": 3.0
                    }
                ]
            }
        ],
        "session_complete": true
    }')

echo "$TASK1_RESPONSE" | jq

echo "$TASK1_RESPONSE" | jq -e '.session_complete == true' >/dev/null
echo "$TASK1_RESPONSE" | jq -e '.experience_complete == false' >/dev/null

SESSION_ID=$(echo "$TASK1_RESPONSE" | jq -r '.saved.session_id')

test "$SESSION_ID" != "null"

echo "🟩 Task 1 completed with session: $SESSION_ID"

echo "🟨 Re-submitting the completed Task 1..."

DUPLICATE_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -w '\n%{http_code}' \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "pattern_recognition_v1",
        "session_id": "'"$SESSION_ID"'",
        "modules": [
            {
                "module_name": "pilot",
                "questions": [
                    {
                        "question_id": "pr_q1",
                        "user_answer": "I",
                        "time_taken_seconds": 3.0
                    },
                    {
                        "question_id": "pr_q2",
                        "user_answer": "30",
                        "time_taken_seconds": 3.0
                    }
                ]
            }
        ],
        "session_complete": true
    }')

HTTP_STATUS=$(printf '%s\n' "$DUPLICATE_RESPONSE" | tail -n 1)
BODY=$(printf '%s\n' "$DUPLICATE_RESPONSE" | sed '$d')

echo "HTTP status: $HTTP_STATUS"

echo "Response:"
printf '%s\n' "$BODY" | jq

test "$HTTP_STATUS" = "409"

printf '%s\n' "$BODY" | jq -e '.error == "task_not_expected"' >/dev/null
printf '%s\n' "$BODY" | jq -e '.expected_task == "strategy_under_constraint_v1"' >/dev/null

echo "🟩 Duplicate Task 1 correctly rejected."

echo "🟢 Duplicate-task negative-path test completed successfully."
