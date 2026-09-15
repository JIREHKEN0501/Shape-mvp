#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"

COOKIE_JAR="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_JAR"
}

trap cleanup EXIT

echo "🟦 Starting canonical participant experience..."

echo "🟨 Giving consent..."

CONSENT_RESPONSE=$(curl -sS \
    -c "$COOKIE_JAR" \
    -X POST "$BASE_URL/consent" \
    -H "Content-Type: application/json")

echo "$CONSENT_RESPONSE" | jq

echo "$CONSENT_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$CONSENT_RESPONSE" | jq -e '.participant_id != null' >/dev/null
echo "$CONSENT_RESPONSE" | jq -e '.experience_id != null' >/dev/null

EXPERIENCE_ID=$(echo "$CONSENT_RESPONSE" | jq -r '.experience_id')

echo "🟩 Loading Task 1..."

TASK1_LOAD_STATUS=$(curl -sS \
    -o /dev/null \
    -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    "$BASE_URL/task/pattern_recognition_v1")

test "$TASK1_LOAD_STATUS" = "200"

echo "🟧 Completing Task 1..."

TASK1_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -X POST "$BASE_URL/participant/submit_result" \
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
echo "$TASK1_RESPONSE" | jq -e '.next_task_id == "strategy_under_constraint_v1"' >/dev/null

echo "🟪 Loading Task 2..."

TASK2_LOAD_STATUS=$(curl -sS \
    -o /dev/null \
    -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    "$BASE_URL/task/strategy_under_constraint_v1")

test "$TASK2_LOAD_STATUS" = "200"

echo "🟥 Completing Task 2..."

TASK2_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -X POST "$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "strategy_under_constraint_v1",
        "modules": [
            {
                "module_name": "pilot",
                "questions": [
                    {
                        "question_id": "suc_q1",
                        "user_answer": "Secure immediate stability",
                        "time_taken_seconds": 3.0
                    },
                    {
                        "question_id": "suc_q2",
                        "user_answer": "Balance speed with safeguards",
                        "time_taken_seconds": 3.0
                    }
                ]
            }
        ],
        "session_complete": true
    }')

echo "$TASK2_RESPONSE" | jq

echo "$TASK2_RESPONSE" | jq -e '.session_complete == true' >/dev/null
echo "$TASK2_RESPONSE" | jq -e '.experience_complete == true' >/dev/null
echo "$TASK2_RESPONSE" | jq -e '.next_task_id == null' >/dev/null

echo "🟫 Fetching experience summary..."

SUMMARY_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    "$BASE_URL/participant/experience/$EXPERIENCE_ID/summary")

echo "$SUMMARY_RESPONSE" | jq

echo "$SUMMARY_RESPONSE" | jq -e '.has_data == true' >/dev/null

echo "🟪 Fetching governed routing trace..."

ROUTING_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    "$BASE_URL/participant/experience/$EXPERIENCE_ID/routing")

echo "$ROUTING_RESPONSE" | jq

echo "$ROUTING_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$ROUTING_RESPONSE" | jq -e '.experience_id == "'"$EXPERIENCE_ID"'"' >/dev/null
echo "$ROUTING_RESPONSE" | jq -e '.routing != null' >/dev/null
echo "$ROUTING_RESPONSE" | jq -e '.trace != null' >/dev/null

echo "✅ Canonical bounded participant experience completed successfully."
