#!/bin/bash
# Helios Auto-Fix Script
# Updates data.json when Helios detects issues
# Usage: ./helios-autofix.sh [operation] [parameters]

DASHBOARD_DIR="/home/chad-yi/.openclaw/workspace/mission-control-dashboard"
HELIOS_DIR="/home/chad-yi/.openclaw/workspace/agents/helios"
LOG_FILE="$HELIOS_DIR/outbox/autofix-log.json"

log_fix() {
    local operation="$1"
    local details="$2"
    local timestamp=$(date -Iseconds)
    
    echo "{\"timestamp\":\"$timestamp\",\"operation\":\"$operation\",\"details\":\"$details\"}" >> "$LOG_FILE"
}

update_agent_status() {
    local agent="$1"
    local newStatus="$2"
    
    cd "$DASHBOARD_DIR"
    
    # Use Python to modify JSON
    python3 << EOF
import json
with open('data.json', 'r') as f:
    data = json.load(f)

# Update agent status
for a in data.get('agents', []):
    if a['id'] == '$agent':
        a['status'] = '$newStatus'
        a['lastUpdated'] = '$timestamp'
        break

with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)
EOF
    
    # Git commit
    git add data.json
    git commit -m "Helios auto-fix: Update $agent status to $newStatus" --quiet
    
    log_fix "update_agent_status" "Changed $agent to $newStatus"
    echo "✅ Updated $agent status to $newStatus"
}

update_lastUpdated() {
    cd "$DASHBOARD_DIR"
    
    timestamp=$(date -Iseconds)
    
    python3 << EOF
import json
with open('data.json', 'r') as f:
    data = json.load(f)

data['lastUpdated'] = '$timestamp'

with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)
EOF
    
    git add data.json
    git commit -m "Helios: Update timestamp" --quiet
    
    log_fix "update_timestamp" "Set lastUpdated to $timestamp"
}

# Main
case "$1" in
    agent-status)
        update_agent_status "$2" "$3"
        ;;
    timestamp)
        update_lastUpdated
        ;;
    *)
        echo "Usage: $0 {agent-status|timestamp} [args...]"
        exit 1
        ;;
esac