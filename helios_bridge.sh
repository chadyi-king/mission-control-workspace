#!/bin/bash
# helios_bridge.sh — Chad's one-liner to POST events to Helios API
#
# Usage:
#   ./helios_bridge.sh <event_type> [json_payload]
#
# Examples:
#   ./helios_bridge.sh heartbeat
#   ./helios_bridge.sh task_update '{"task_id":"A6-3","status":"done"}'
#   ./helios_bridge.sh message '{"text":"Session started"}'
#
# Event types: heartbeat, task_create, task_update, task_ack,
#              agent_update, agent_command, message, status_request

HELIOS_API="https://helios-api-xfvi.onrender.com"
AGENT="${OPENCLAW_AGENT_NAME:-chad-yi}"
EVENT_TYPE="${1:-heartbeat}"
PAYLOAD_ARG="${2:-{}}"

# Build timestamp
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build full event JSON
BODY=$(cat <<JSON
{
  "agent": "${AGENT}",
  "event_type": "${EVENT_TYPE}",
  "status": "success",
  "idempotency_key": "$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen 2>/dev/null || echo "$(date +%s%N)")",
  "payload": ${PAYLOAD_ARG},
  "model_tier": "cheap",
  "model_id": "kimi-k2p5",
  "reasoning_summary": "",
  "confidence": 0.9,
  "ts": "${TS}"
}
JSON
)

echo "[helios_bridge] → POST ${HELIOS_API}/api/events"
echo "[helios_bridge]   event_type: ${EVENT_TYPE}"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "${HELIOS_API}/api/events" \
  -H "Content-Type: application/json" \
  -d "${BODY}" \
  --max-time 15)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY_RESP=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "[helios_bridge] ✓ Accepted (200)"
else
  echo "[helios_bridge] ✗ Error ${HTTP_CODE}: ${BODY_RESP}"
fi
