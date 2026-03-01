#!/bin/bash
# Helios Proactive Auditor Runner
# Spawns Helios with full tool access every 15 minutes

GATEWAY_URL="${GATEWAY_URL:-http://localhost:3000}"
GATEWAY_TOKEN="${GATEWAY_TOKEN:-}"

echo "[$(date)] Spawning Helios for proactive audit..."

# Spawn Helios as isolated agent with helios-audit skill
curl -X POST "${GATEWAY_URL}/v1/sessions/spawn" \
  -H "Authorization: Bearer ${GATEWAY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "helios",
    "label": "helios-proactive-audit-'$(date +%s)'",
    "task": "Run proactive Mission Control audit using helios-audit skill.\n\n1. Screenshot https://mission-control-dashboard-hf0r.onrender.com/\n2. Verify all sections show real data (not 0s)\n3. Check agent heartbeats and outboxes\n4. Verify data.json integrity\n5. If ANY issues found: message CHAD_YI immediately with screenshot and details\n6. If clean: report success to outbox only\n\nBe suspicious. Verify everything. Screenshot always.",
    "timeoutSeconds": 600,
    "model": "ollama/qwen2.5:7b",
    "skills": ["helios-audit", "browser"]
  }'

echo "[$(date)] Helios spawned. Will check results in 15 minutes."
