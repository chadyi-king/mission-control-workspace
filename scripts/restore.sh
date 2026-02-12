#!/bin/bash
# restore.sh
# Restores data.json from backup

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-filename>"
    echo ""
    echo "Available backups:"
    /home/chad-yi/.openclaw/workspace/scripts/list-backups.sh
    exit 1
fi

BACKUP_FILE="$1"
DATA_FILE="/home/chad-yi/.openclaw/workspace/DATA/data.json"

# Check if backup exists
if [ ! -f "$BACKUP_FILE" ]; then
    # Try in backup directories
    if [ -f "/home/chad-yi/.openclaw/workspace/DATA/backups/manual/$BACKUP_FILE" ]; then
        BACKUP_FILE="/home/chad-yi/.openclaw/workspace/DATA/backups/manual/$BACKUP_FILE"
    elif [ -f "/home/chad-yi/.openclaw/workspace/DATA/backups/auto/$BACKUP_FILE" ]; then
        BACKUP_FILE="/home/chad-yi/.openclaw/workspace/DATA/backups/auto/$BACKUP_FILE"
    else
        echo "ERROR: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

echo "Restoring from: $BACKUP_FILE"

# Create safety backup of current
cp "$DATA_FILE" "$DATA_FILE.bak.$(date +%s)"

# Restore
cp "$BACKUP_FILE" "$DATA_FILE"

# Verify
echo ""
echo "Verifying restored data..."
python3 /home/chad-yi/.openclaw/workspace/scripts/verify-data.py

echo ""
echo "✅ Restore complete"
echo "   If something is wrong, current data backed up to: $DATA_FILE.bak.*"
