#!/bin/bash
set -e

echo "[1] Requesting /decoy to obtain hp_field cookie..."
curl -s -i -c cookies.txt http://127.0.0.1:5000/decoy > /dev/null

echo "[2] Extracting hp_field name..."
hp_name=$(grep hp_field cookies.txt | awk '{print $6}')
hp_value=$(grep hp_field cookies.txt | awk '{print $7}')

echo "   -> hp_field name: $hp_name"
echo "   -> hp_field value: $hp_value"

echo "[3] Sending honeypot trigger to /snare..."
curl -i -b cookies.txt -H "Content-Type: application/json" \
     -d "{\"ts\": 123, \"elapsed_ms\": 3, \"ua\": \"bot-test\"}" \
     http://127.0.0.1:5000/snare

echo ""
echo "[4] Tailing audit_log.jsonl..."
tail -n 10 logs/audit_log.jsonl
echo "[done]"

