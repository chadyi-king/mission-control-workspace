#!/bin/bash
# list-backups.sh
# Lists available backups for recovery

echo "=== MANUAL BACKUPS (Before Changes) ==="
ls -lt /home/chad-yi/.openclaw/workspace/DATA/backups/manual/ 2>/dev/null | head -15 || echo "No manual backups"

echo ""
echo "=== AUTO BACKUPS (Hourly) ==="
ls -lt /home/chad-yi/.openclaw/workspace/DATA/backups/auto/ 2>/dev/null | head -10 || echo "No auto backups"
