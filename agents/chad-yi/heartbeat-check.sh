#!/bin/bash
# CHAD_YI Heartbeat - Self-monitoring system
# Runs automatically to check inbox and report status

INBOX="/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox"
LOG="/home/chad-yi/.openclaw/workspace/agents/chad-yi/heartbeat.log"
URGENT_FILE="/home/chad-yi/.openclaw/workspace/agents/chad-yi/URGENT_PENDING.flag"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] CHAD_YI Heartbeat" >> "$LOG"

# Count unread messages
MSG_COUNT=$(ls -1 "$INBOX"/*.md 2>/dev/null | wc -l)
echo "  Inbox messages: $MSG_COUNT" >> "$LOG"

# Check for URGENT messages
URGENT_COUNT=$(ls -1 "$INBOX"/URGENT* 2>/dev/null | wc -l)
echo "  URGENT messages: $URGENT_COUNT" >> "$LOG"

# Check for digests
DIGEST_COUNT=$(ls -1 "$INBOX"/digest* 2>/dev/null | wc -l)
echo "  Digests unread: $DIGEST_COUNT" >> "$LOG"

# Check for Helios alerts
ALERT_COUNT=$(ls -1 "$INBOX"/helios-alert* 2>/dev/null | wc -l)
echo "  Helios alerts: $ALERT_COUNT" >> "$LOG"

# Check for Cerebronn plans
PLAN_COUNT=$(ls -1 "$INBOX"/cerebronn-plan* 2>/dev/null | wc -l)
echo "  Cerebronn plans: $PLAN_COUNT" >> "$LOG"

# If any urgent or critical, create flag file
if [ "$URGENT_COUNT" -gt 0 ] || [ "$ALERT_COUNT" -gt 0 ]; then
    echo "URGENT items pending: $((URGENT_COUNT + ALERT_COUNT))" > "$URGENT_FILE"
    echo "  ⚠️  URGENT items detected - need Caleb attention" >> "$LOG"
else
    rm -f "$URGENT_FILE"
    echo "  ✅ No urgent items" >> "$LOG"
fi

# If more than 20 messages, flag for processing
if [ "$MSG_COUNT" -gt 20 ]; then
    echo "  ⚠️  INBOX BACKLOG: $MSG_COUNT messages unread" >> "$LOG"
    echo "INBOX_BACKLOG: $MSG_COUNT" > "$INBOX/../INBOX_BACKLOG.flag"
fi

echo "  Heartbeat complete" >> "$LOG"
echo "" >> "$LOG"
