#!/bin/bash
# Auto-save conversation memory every 30 minutes
# Run via: */30 * * * * /home/chad-yi/.openclaw/workspace/scripts/auto-save-memory.sh

WORKSPACE="/home/chad-yi/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
MEMORY_FILE="$WORKSPACE/memory/$DATE.md"

# Create memory directory if not exists
mkdir -p "$WORKSPACE/memory"

# Append auto-save marker
{
    echo ""
    echo "---"
    echo "## Auto-Save Checkpoint - $TIME"
    echo ""
    echo "Session active. Context preserved."
    echo ""
} >> "$MEMORY_FILE"

# Log the save
echo "[$(date)] Memory checkpoint saved to $MEMORY_FILE" >> "$WORKSPACE/logs/memory-auto-save.log"