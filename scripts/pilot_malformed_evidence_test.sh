#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-127.0.0.1:5000}"

COOKIE_JAR="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_JAR"
}

trap cleanup EXIT

echo "🟦 Starting malformed-evidence negative-path test..."

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

echo "🟨 Attempting correctly ordered task with malformed evidence..."

RESPONSE=$(curl -sS \
    -b "$COOKIE_JAR" \
    -w '\n%{http_code}' \
    -X POST "http://$BASE_URL/participant/submit_result" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "pattern_recognition_v1",
        "modules": [
            {
                "module_name": "pattern_round_1",
                "questions": [
                    {
                        "user_answer": "invalid-but-present",
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

test "$HTTP_STATUS" = "400"

echo "🟨 Verifying rejection audit..."

AUDIT_MATCH=$(grep '"action": "task_evidence_rejected"' logs/audit_log.jsonl | grep "$EXPERIENCE_ID" | tail -n 1 || true)

test -n "$AUDIT_MATCH"

echo "$AUDIT_MATCH" | jq -e '.action == "task_evidence_rejected"' >/dev/null
echo "$AUDIT_MATCH" | jq -e '.status == "rejected"' >/dev/null
echo "$AUDIT_MATCH" | jq -e '.subject == "'"$EXPERIENCE_ID"'"' >/dev/null
echo "$AUDIT_MATCH" | jq -e '.extra.task_id == "pattern_recognition_v1"' >/dev/null
echo "$AUDIT_MATCH" | jq -e '.extra.validation_type == "cognitive"' >/dev/null

if echo "$AUDIT_MATCH" | grep -q 'invalid-but-present'; then
    echo "🔴 Rejected answer leaked into audit record."
    exit 1
fi

echo "🟩 Rejection audit verified without answer leakage."
echo "🟩 Malformed evidence correctly rejected."
echo "🟢 Malformed-evidence negative-path test completed successfully."
