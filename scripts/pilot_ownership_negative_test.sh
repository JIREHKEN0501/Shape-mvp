#!/bin/bash

set -euo pipefail

BASE_URL="${BASE_URL:-127.0.0.1:5000}"

COOKIE_A="$(mktemp)"
COOKIE_B="$(mktemp)"
COOKIE_ATTACK="$(mktemp)"

cleanup() {
    rm -f "$COOKIE_A" "$COOKIE_B" "$COOKIE_ATTACK"
}

trap cleanup EXIT

echo "🟦 Starting ownership-isolation negative-path test..."

echo "🟨 Creating Participant A..."

CONSENT_A=$(curl -sS \
    -c "$COOKIE_A" \
    -X POST "http://$BASE_URL/consent" \
    -H "Content-Type: application/json")

echo "$CONSENT_A" | jq

echo "$CONSENT_A" | jq -e '.ok == true' >/dev/null
echo "$CONSENT_A" | jq -e '.participant_id != null' >/dev/null
echo "$CONSENT_A" | jq -e '.experience_id != null' >/dev/null

PARTICIPANT_A=$(echo "$CONSENT_A" | jq -r '.participant_id')
EXPERIENCE_A=$(echo "$CONSENT_A" | jq -r '.experience_id')

echo "🟩 Participant A: $PARTICIPANT_A"
echo "🟩 Experience A: $EXPERIENCE_A"

echo "🟨 Creating Participant B..."

CONSENT_B=$(curl -sS \
    -c "$COOKIE_B" \
    -X POST "http://$BASE_URL/consent" \
    -H "Content-Type: application/json")

echo "$CONSENT_B" | jq

echo "$CONSENT_B" | jq -e '.ok == true' >/dev/null
echo "$CONSENT_B" | jq -e '.participant_id != null' >/dev/null
echo "$CONSENT_B" | jq -e '.experience_id != null' >/dev/null

PARTICIPANT_B=$(echo "$CONSENT_B" | jq -r '.participant_id')
EXPERIENCE_B=$(echo "$CONSENT_B" | jq -r '.experience_id')

echo "🟩 Participant B: $PARTICIPANT_B"
echo "🟩 Experience B: $EXPERIENCE_B"

test "$PARTICIPANT_A" != "$PARTICIPANT_B"
test "$EXPERIENCE_A" != "$EXPERIENCE_B"

echo "🟨 Replacing only Participant A's experience cookie with Participant B's..."

# Preserve A's participant_id cookie while deliberately substituting B's
# experience_id into a separate attack cookie jar.
awk -F '\t' '
$6 == "participant_id" {
    print
}
' "$COOKIE_A" > "$COOKIE_ATTACK"

printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "#HttpOnly_127.0.0.1" \
    "FALSE" \
    "/" \
    "FALSE" \
    "2147483647" \
    "experience_id" \
    "$EXPERIENCE_B" >> "$COOKIE_ATTACK"

echo "🟨 Participant A attempting to submit against Participant B's experience..."

RESPONSE=$(curl -sS \
    -b "$COOKIE_ATTACK" \
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

HTTP_STATUS=$(printf '%s\n' "$RESPONSE" | tail -n 1)
BODY=$(printf '%s\n' "$RESPONSE" | sed '$d')

echo "HTTP status: $HTTP_STATUS"
echo "Response:"
printf '%s\n' "$BODY" | jq

test "$HTTP_STATUS" = "403"
printf '%s\n' "$BODY" | jq -e '.error == "experience_not_owned"' >/dev/null

echo "🟩 Cross-participant experience context correctly rejected."

echo "🟨 Verifying ownership-rejection audit..."

AUDIT_MATCH=$(jq -c \
    --arg experience "$EXPERIENCE_B" \
    --arg participant "$PARTICIPANT_A" \
    'select(
        .action == "experience_membership_rejected" and
        .subject == $experience and
        .actor == ("participant:" + $participant)
    )' \
    logs/audit_log.jsonl | tail -n 1)

test -n "$AUDIT_MATCH"

echo "$AUDIT_MATCH" | jq -e '.status == "rejected"' >/dev/null
echo "$AUDIT_MATCH" | jq -e '.extra.notes == "experience_does_not_belong_to_participant"' >/dev/null

echo "🟩 Ownership rejection audit verified."

echo "🟢 Ownership-isolation negative-path test completed successfully."
