#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-127.0.0.1:5000}"

COOKIE_JAR="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_JAR"
}

trap cleanup EXIT

echo "🟦 Starting negative-path participant experience..."

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

echo "🟨 Attempting out-of-order task submission..."

RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -w '\n%{http_code}' \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "strategy_under_constraint_v1",
        "modules": [
            {
                "module_name": "allocation_round_1",
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

HTTP_STATUS=$(printf '%s\n' "$RESPONSE" | tail -n 1)
BODY=$(printf '%s\n' "$RESPONSE" | sed '$d')

echo "HTTP status: $HTTP_STATUS"
echo "Response:"
printf '%s\n' "$BODY" | jq

test "$HTTP_STATUS" = "409"

printf '%s\n' "$BODY" | jq -e '.error == "task_not_expected"' >/dev/null
printf '%s\n' "$BODY" | jq -e '.expected_task == "pattern_recognition_v1"' >/dev/null

echo "🟩 Out-of-order task correctly rejected."

echo "🟢 Negative-path pilot test completed successfully."
