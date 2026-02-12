#!/bin/bash
# backup-before-change.sh
# Creates backup before ANY data.json change

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REASON="${1:-MANUAL}"
DATA_FILE="/home/chad-yi/.openclaw/workspace/DATA/data.json"
BACKUP_DIR="/home/chad-yi/.openclaw/workspace/DATA/backups/manual"

# Create backup filename
BACKUP_FILE="$BACKUP_DIR/data-$TIMESTAMP-$REASON.json"

# Check if data file exists
if [ ! -f "$DATA_FILE" ]; then
    echo "ERROR: data.json not found at $DATA_FILE"
    exit 1
fi

# Create backup
cp "$DATA_FILE" "$BACKUP_FILE"

# Verify backup exists and has content
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup failed - file is empty"
    exit 1
fi

# Count tasks in backup
TASK_COUNT=$(python3 -c "import json; print(len(json.load(open('$BACKUP_FILE'))['tasks']))")

echo "✅ Backup created: $BACKUP_FILE"
echo "   Tasks: $TASK_COUNT"
echo "   Reason: $REASON"
