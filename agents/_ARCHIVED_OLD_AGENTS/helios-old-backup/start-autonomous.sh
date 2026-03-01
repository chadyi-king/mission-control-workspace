#!/bin/bash
# Helios Autonomous Auditor - Continuous Operation
# This keeps Helios running as a live agent, not cron

LOG_FILE="/home/chad-yi/.openclaw/workspace/agents/helios/helios.log"
PID_FILE="/home/chad-yi/.openclaw/workspace/agents/helios/helios.pid"

echo "[$(date)] Starting Helios Autonomous Auditor..." >> $LOG_FILE

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "[$(date)] Helios already running (PID: $OLD_PID)" >> $LOG_FILE
        exit 0
    fi
fi

# Start continuous loop
while true; do
    echo "[$(date)] Helios heartbeat - checking dashboard..." >> $LOG_FILE
    
    # Spawn Helios for this audit cycle
    openclaw sessions_spawn \
        --agentId helios \
        --label "helios-autonomous-$(date +%s)" \
        --task "You are Helios in AUTONOMOUS MODE.\n\nCURRENT STATUS:\n- You are actively monitoring Mission Control\n- You're collaborating with CHAD_YI\n- You have full tool access\n\nYOUR AUTONOMOUS ACTIONS:\n1. Screenshot all 5 dashboard pages\n2. Check for any issues (0s, empty data, errors)\n3. If issues found:\n   - Try to auto-fix if possible\n   - If can't auto-fix: sessions_send to CHAD_YI with details and screenshot\n   - Work WITH CHAD_YI to fix it\n   - Only escalate to Caleb if CHAD_YI is blocked\n4. If no issues: Log success, continue monitoring\n5. Check CHAD_YI's recent work - verify his fixes worked\n\nCOLLABORATION RULES:\n- You and CHAD_YI are a team\n- Find issues together, fix together\n- You have browser/tools, he has full system access\n- Combine capabilities to solve problems\n- Report success/failure to CHAD_YI\n\nAUTONOMOUS DECISIONS YOU CAN MAKE:\n- Update data.json timestamps\n- Recalculate task counts\n- Ping agents for status\n- Screenshot and document issues\n- Work with CHAD_YI on fixes\n\nDO NOT:\n- Message Caleb directly (always through CHAD_YI)\n- Make changes that need Caleb's approval without asking CHAD_YI\n- Leave issues unreported\n\nRun audit now. Report to CHAD_YI when done." \
        --timeoutSeconds 600 \
        --model ollama/qwen2.5:7b &
    
    HELIOS_PID=$!
    echo $HELIOS_PID > $PID_FILE
    
    # Wait for completion (max 10 minutes)
    wait $HELIOS_PID
    
    echo "[$(date)] Audit cycle complete. Sleeping 15 minutes..." >> $LOG_FILE
    
    # Sleep 15 minutes before next cycle
    sleep 900
done