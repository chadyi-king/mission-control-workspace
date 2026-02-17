#!/bin/bash
# Helios Bridge - Run from HEARTBEAT.md or manually
# Pulls messages from remote Helios and routes to local message bus

cd /home/chad-yi/.openclaw/workspace

# Pull latest from GitHub
echo "[BRIDGE] Pulling from GitHub..."
git pull origin main 2>/dev/null || echo "[BRIDGE] Git pull skipped (no remote or already up to date)"

# Run the bridge
python3 agents/message-bridge/helios_bridge.py

# If there are messages from CHAD_YI to send, commit and push
if [ -d "messages/chad-yi/outbox" ] && [ "$(ls -A messages/chad-yi/outbox 2>/dev/null)" ]; then
    echo "[BRIDGE] Pushing responses to Helios..."
    git add messages/chad-yi/outbox/
    git commit -m "CHAD_YI messages for Helios - $(date +%Y-%m-%d-%H:%M)" 2>/dev/null
    git push origin main 2>/dev/null || echo "[BRIDGE] Push failed (check credentials)"
fi

echo "[BRIDGE] Done"
