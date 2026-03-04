#!/bin/bash
# CHAD_YI Report to Caleb - FIXED VERSION
# Creates report files that CHAD_YI will actually read and send

REPORT_TIME=$1
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')
LOG="/home/chad-yi/.openclaw/workspace/agents/chad-yi/report-to-caleb.log"

echo "[$TIME] Generating $REPORT_TIME report" >> "$LOG"

# Create report file for CHAD_YI to read
REPORT_FILE="/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/REPORT-${TIME}-${REPORT_TIME}.md"

# Get agent status
CEREBRONN=$(systemctl --user is-active cerebronn 2>/dev/null || echo "inactive")
HELIOS=$(systemctl --user is-active helios 2>/dev/null || echo "inactive")
FORGER=$(systemctl --user is-active forger 2>/dev/null || echo "inactive")
QUANTA=$(systemctl --user is-active quanta-v3 2>/dev/null || echo "inactive")

# Get latest data
cd /home/chad-yi/.openclaw/workspace

# Count tasks from data.json
TOTAL=$(cat mission-control-dashboard/data.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('tasks',{})))" 2>/dev/null || echo "unknown")

cat > "$REPORT_FILE" << EOF
# 📊 Agent Status Report — ${TIME} SGT

## Task Overview
• **Total Tasks:** $TOTAL

## Agent Status
| Agent | Status | Details |
|-------|--------|---------|
| Cerebronn | ${CEREBRONN} | Deep reasoning / architecture |
| Helios | ${HELIOS} | Mission Control auditing |
| Forger | ${FORGER} | Website building |
| Quanta | ${QUANTA} | Trading (XAUUSD) |

## Current Time
**${DATE} ${TIME} SGT**

---
*Auto-generated report*
EOF

echo "[$TIME] Report created: $REPORT_FILE" >> "$LOG"
