#!/bin/bash
# Checkpoint every 4 hours - captures key context
# Run via: 0 */4 * * * /home/chad-yi/.openclaw/workspace/scripts/4hr-checkpoint.sh

WORKSPACE="/home/chad-yi/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
HOUR=$(date +%H)
MEMORY_FILE="$WORKSPACE/memory/$DATE.md"
DASHBOARD_FILE="$WORKSPACE/mission-control-dashboard/data.json"

mkdir -p "$WORKSPACE/memory"

# Determine period of day
if [ "$HOUR" -lt 12 ]; then
    PERIOD="Morning"
elif [ "$HOUR" -lt 16 ]; then
    PERIOD="Afternoon"
elif [ "$HOUR" -lt 20 ]; then
    PERIOD="Evening"
else
    PERIOD="Night"
fi

# Get current stats from dashboard if available
if [ -f "$DASHBOARD_FILE" ]; then
    TOTAL=$(grep -o '"totalTasks": [0-9]*' "$DASHBOARD_FILE" | head -1 | grep -o '[0-9]*')
    PENDING=$(grep -o '"pending": [0-9]*' "$DASHBOARD_FILE" | head -1 | grep -o '[0-9]*')
    DONE=$(grep -o '"done": [0-9]*' "$DASHBOARD_FILE" | head -1 | grep -o '[0-9]*')
    STATS="Tasks: Total $TOTAL | Pending $PENDING | Done $DONE"
else
    STATS="Dashboard data unavailable"
fi

# Write checkpoint
{
    echo ""
    echo "---"
    echo "## $PERIOD Checkpoint - $TIME"
    echo ""
    echo "**Session:** Active"
    echo "**Dashboard:** $STATS"
    echo "**Status:** Context preserved"
    echo ""
} >> "$MEMORY_FILE"

echo "[$(date)] $PERIOD checkpoint saved" >> "$WORKSPACE/logs/checkpoints.log"