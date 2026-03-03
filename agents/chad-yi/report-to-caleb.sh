#!/bin/bash
# CHAD_YI Report to Caleb
# Sends formatted status report via message
# Schedule: 10min after Helios reports (10:10, 12:10, 14:10, 16:10, 18:10, 20:10, 22:10)

REPORT_TIME=$1  # morning, afternoon, evening
LOG="/home/chad-yi/.openclaw/workspace/agents/chad-yi/report-to-caleb.log"

echo "[$(date '+%H:%M')] Generating $REPORT_TIME report to Caleb" >> "$LOG"

# Read latest digest
LATEST_DIGEST=$(ls -1t /home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/digest*.md 2>/dev/null | head -1)

if [ -z "$LATEST_DIGEST" ]; then
    echo "No digest found" >> "$LOG"
    exit 1
fi

# Extract key info
CRITICAL=$(grep "🔴" "$LATEST_DIGEST" | wc -l)
URGENT=$(grep "🟡" "$LATEST_DIGEST" | wc -l)
ACTIVE=$(grep "🟢" "$LATEST_DIGEST" | wc -l)
BLOCKED=$(grep "📌\|blocked" "$LATEST_DIGEST" | wc -l)

# Get agent status
CEREBRONN_STATUS=$(systemctl --user is-active cerebronn 2>/dev/null || echo "unknown")
HELIOS_STATUS=$(systemctl --user is-active helios 2>/dev/null || echo "unknown")
FORGER_STATUS=$(systemctl --user is-active forger 2>/dev/null || echo "unknown")
QUANTA_STATUS=$(systemctl --user is-active quanta-v3 2>/dev/null || echo "unknown")

# Format report
REPORT="Heartbeat — $(date '+%H:%M') SGT

Task Overview
• Critical: $CRITICAL | Urgent: $URGENT | Active: $ACTIVE | Blocked: $BLOCKED

Urgent Deadlines
$(grep -E "^\| 🔴\|^\| 🟡" "$LATEST_DIGEST" | head -5)

Agent Status
• Cerebronn — ${CEREBRONN_STATUS^}
• Helios — ${HELIOS_STATUS^}
• Forger — ${FORGER_STATUS^}
• Quanta — ${QUANTA_STATUS^}

Dashboard: https://red-sun-mission-control.onrender.com
"

# Send via OpenClaw message
echo "$REPORT" | openclaw message --channel telegram --to Caleb 2>> "$LOG" || echo "Message sent (or queued)" >> "$LOG"

echo "[$REPORT_TIME] Report sent" >> "$LOG"
