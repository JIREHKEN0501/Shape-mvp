#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-127.0.0.1:5000}"

COOKIE_JAR="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_JAR"
}

trap cleanup EXIT

echo "🟦 Starting adaptive participant experience..."

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
BOUNDED_EXPERIENCE_ID=$(echo "$CONSENT_RESPONSE" | jq -r '.experience_id')

echo "🟩 Consent established for participant: $PARTICIPANT_ID"
echo "🟩 Bounded experience created: $BOUNDED_EXPERIENCE_ID"

echo "🟨 Authorizing adaptive routing..."

ADAPTIVE_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -c "$COOKIE_JAR" \
    -X POST "http://$BASE_URL/participant/adaptive/authorize" \
    -H "Content-Type: application/json")

echo "$ADAPTIVE_RESPONSE" | jq

echo "$ADAPTIVE_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$ADAPTIVE_RESPONSE" | jq -e '.participant_id == "'"$PARTICIPANT_ID"'"' >/dev/null
echo "$ADAPTIVE_RESPONSE" | jq -e '.experience_id != null' >/dev/null
echo "$ADAPTIVE_RESPONSE" | jq -e '.mode == "adaptive"' >/dev/null
echo "$ADAPTIVE_RESPONSE" | jq -e '.adaptive_authorized == true' >/dev/null

ADAPTIVE_EXPERIENCE_ID=$(echo "$ADAPTIVE_RESPONSE" | jq -r '.experience_id')

test "$ADAPTIVE_EXPERIENCE_ID" != "$BOUNDED_EXPERIENCE_ID"

echo "🟩 Explicit adaptive authorization confirmed."
echo "🟩 Adaptive experience created: $ADAPTIVE_EXPERIENCE_ID"

echo "🟦 Loading canonical Task 1..."

TASK1_LOAD_STATUS=$(curl -sS \
    -o /dev/null \
    -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    "http://$BASE_URL/task/pattern_recognition_v1")

test "$TASK1_LOAD_STATUS" = "200"

echo "🟧 Completing canonical Task 1..."

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

echo "🟪 Requesting first adaptive task..."

ADAPTIVE_TASK1_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    "http://$BASE_URL/tasks/next/$PARTICIPANT_ID")

echo "$ADAPTIVE_TASK1_RESPONSE" | jq

echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.adaptive_execution == true' >/dev/null
echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.experience_id == "'"$ADAPTIVE_EXPERIENCE_ID"'"' >/dev/null
echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.task.task_id != null' >/dev/null

SELECTED_TASK1_ID=$(echo "$ADAPTIVE_TASK1_RESPONSE" | jq -r '.task.task_id')

echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.task.category != null' >/dev/null
echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.task.difficulty != null' >/dev/null
echo "$ADAPTIVE_TASK1_RESPONSE" | jq -e '.task.meta != null or .meta != null' >/dev/null

echo "🟩 Adaptive execution confirmed."
echo "🟩 Selected adaptive Task 1: $SELECTED_TASK1_ID"

echo "🟦 Selected adaptive Task 1 payload:"
echo "$ADAPTIVE_TASK1_RESPONSE" | jq '.task'

echo "🟧 Completing adaptive Task 1..."

SELECTED_TASK1_ANSWER=$(jq -r \
    --arg task_id "$SELECTED_TASK1_ID" \
    '.tasks[] | select(.task_id == $task_id) | .answer' \
    project/schemas/task_catalog.json)

test -n "$SELECTED_TASK1_ANSWER"
test "$SELECTED_TASK1_ANSWER" != "null"

echo "🟩 Canonical answer resolved for $SELECTED_TASK1_ID."

ADAPTIVE_SUBMIT1_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "'"$SELECTED_TASK1_ID"'",
        "answer": "'"$SELECTED_TASK1_ANSWER"'",
        "latency_ms": 3000,
        "session_complete": true
    }')

echo "RAW ADAPTIVE SUBMISSION RESPONSE:"
printf '%s\n' "$ADAPTIVE_SUBMIT1_RESPONSE"

echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq

echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq -e '.session_complete == true' >/dev/null
echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq -e '.experience_complete == false' >/dev/null
echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq -e '.metrics.type == "single_task"' >/dev/null
echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq -e '.metrics.valid_task == true' >/dev/null
echo "$ADAPTIVE_SUBMIT1_RESPONSE" | jq -e '.metrics.is_correct == true' >/dev/null

echo "🟩 Adaptive Task 1 scored correctly."

echo "🟪 Requesting second adaptive task..."

ADAPTIVE_TASK2_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    "http://$BASE_URL/tasks/next/$PARTICIPANT_ID")

echo "$ADAPTIVE_TASK2_RESPONSE" | jq

echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.adaptive_execution == true' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.experience_id == "'"$ADAPTIVE_EXPERIENCE_ID"'"' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.task.task_id != null' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.task.category != null' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.task.difficulty != null' >/dev/null
echo "$ADAPTIVE_TASK2_RESPONSE" | jq -e '.task.meta != null or .meta != null' >/dev/null

SELECTED_TASK2_ID=$(echo "$ADAPTIVE_TASK2_RESPONSE" | jq -r '.task.task_id')

echo "🟩 Second adaptive execution confirmed."
echo "🟩 Selected adaptive Task 2: $SELECTED_TASK2_ID"

echo "🟦 Selected adaptive Task 2 payload:"
echo "$ADAPTIVE_TASK2_RESPONSE" | jq '.task'

echo "🟧 Completing adaptive Task 2..."

SELECTED_TASK2_ANSWER=$(jq -r \
    --arg task_id "$SELECTED_TASK2_ID" \
    '.tasks[] | select(.task_id == $task_id) | .answer' \
    project/schemas/task_catalog.json)

test -n "$SELECTED_TASK2_ANSWER"
test "$SELECTED_TASK2_ANSWER" != "null"

echo "🟩 Canonical answer resolved for $SELECTED_TASK2_ID."

ADAPTIVE_SUBMIT2_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "'"$SELECTED_TASK2_ID"'",
        "answer": "'"$SELECTED_TASK2_ANSWER"'",
        "latency_ms": 3000,
        "session_complete": true
    }')

echo "RAW ADAPTIVE SUBMISSION RESPONSE:"
printf '%s\n' "$ADAPTIVE_SUBMIT2_RESPONSE"

echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq

echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq -e '.session_complete == true' >/dev/null
echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq -e '.experience_complete == false' >/dev/null
echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq -e '.metrics.type == "single_task"' >/dev/null
echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq -e '.metrics.valid_task == true' >/dev/null
echo "$ADAPTIVE_SUBMIT2_RESPONSE" | jq -e '.metrics.is_correct == true' >/dev/null

echo "🟩 Adaptive Task 2 scored correctly."

echo "🟪 Requesting post-submission adaptive progression..."

ADAPTIVE_TASK3_RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    "http://$BASE_URL/tasks/next/$PARTICIPANT_ID")

echo "$ADAPTIVE_TASK3_RESPONSE" | jq

echo "$ADAPTIVE_TASK3_RESPONSE" | jq -e '.ok == true' >/dev/null
echo "$ADAPTIVE_TASK3_RESPONSE" | jq -e '.adaptive_execution == true' >/dev/null
echo "$ADAPTIVE_TASK3_RESPONSE" | jq -e '.experience_id == "'"$ADAPTIVE_EXPERIENCE_ID"'"' >/dev/null
echo "$ADAPTIVE_TASK3_RESPONSE" | jq -e '.task.task_id != null' >/dev/null

echo "🟩 Adaptive progression remains executable after two scored tasks."

echo "🟢 Adaptive pilot harness completed successfully."
