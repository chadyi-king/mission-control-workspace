#!/bin/bash
# CHAD_YI Inbox Processor - Read and summarize messages
# Should be triggered by heartbeat or run manually

INBOX="/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox"
REPORT="/home/chad-yi/.openclaw/workspace/agents/chad-yi/INBOX_REPORT.md"

echo "# CHAD_YI Inbox Report - $(date '+%Y-%m-%d %H:%M')" > "$REPORT"
echo "" >> "$REPORT"

# Process URGENT messages first
echo "## 🔴 URGENT ITEMS" >> "$REPORT"
echo "" >> "$REPORT"
for urgent in "$INBOX"/URGENT*.md; do
    if [ -f "$urgent" ]; then
        echo "### $(basename "$urgent")" >> "$REPORT"
        head -20 "$urgent" >> "$REPORT"
        echo "" >> "$REPORT"
    fi
done

# Process digests
echo "## 📊 Latest Digest" >> "$REPORT"
echo "" >> "$REPORT"
LATEST_DIGEST=$(ls -1t "$INBOX"/digest*.md 2>/dev/null | head -1)
if [ -n "$LATEST_DIGEST" ]; then
    cat "$LATEST_DIGEST" >> "$REPORT"
else
    echo "No digest found" >> "$REPORT"
fi
echo "" >> "$REPORT"

# Process Helios alerts
echo "## 🚨 Helios Alerts" >> "$REPORT"
echo "" >> "$REPORT"
for alert in "$INBOX"/helios-alert*.md; do
    if [ -f "$alert" ]; then
        echo "- $(basename "$alert")" >> "$REPORT"
        head -5 "$alert" | grep -E "Agent:|Silent" >> "$REPORT"
    fi
done
echo "" >> "$REPORT"

# Count total
echo "## 📈 Summary" >> "$REPORT"
echo "" >> "$REPORT"
echo "- Total messages: $(ls -1 "$INBOX"/*.md 2>/dev/null | wc -l)" >> "$REPORT"
echo "- URGENT: $(ls -1 "$INBOX"/URGENT*.md 2>/dev/null | wc -l)" >> "$REPORT"
echo "- Digests: $(ls -1 "$INBOX"/digest*.md 2>/dev/null | wc -l)" >> "$REPORT"
echo "- Cerebronn plans: $(ls -1 "$INBOX"/cerebronn-plan*.md 2>/dev/null | wc -l)" >> "$REPORT"
echo "" >> "$REPORT"

echo "Report generated: $REPORT"
