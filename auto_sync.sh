#!/bin/bash
# Auto-sync script for CHAD_YI to coordinate with Helios
# Runs every 30 seconds: pulls updates, processes messages, pushes responses

cd /home/chad-yi/.openclaw/workspace

echo "[$(date)] CHAD_YI Auto-Sync Starting..."

while true; do
    # Pull latest from Helios
    git pull upstream master --quiet 2>/dev/null
    
    # Check for messages from Helios
    if ls messages/chad-yi/inbox/*.json 1> /dev/null 2>&1; then
        echo "[$(date)] New messages from Helios:"
        for msg in messages/chad-yi/inbox/*.json; do
            echo "  - $(basename $msg)"
            # Process message here (could call Python script)
            cat "$msg" | jq -r '.subject' 2>/dev/null
            # Move to archive after processing
            mv "$msg" messages/chad-yi/archive/ 2>/dev/null || true
        done
    fi
    
    # Check if I have messages to send
    if ls messages/chad-yi/outbox/*.json 1> /dev/null 2>&1; then
        echo "[$(date)] Pushing messages to Helios..."
        git add messages/chad-yi/outbox/ --quiet
        git commit -m "CHAD_YI auto-sync: $(date +%H:%M:%S)" --quiet
        git push upstream master --quiet 2>/dev/null
    fi
    
    # Wait 30 seconds
    sleep 30
done
