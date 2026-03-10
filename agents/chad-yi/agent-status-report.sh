#!/bin/bash
# CHAD_YI Agent Status Report - Shows what agents are DOING

REPORT_TIME=$(date '+%H:%M')
LOG_DIR="/home/chad-yi/.openclaw/workspace/agents"

echo "Agent Status — $REPORT_TIME SGT"
echo ""

# CEREBRONN
echo "🧠 CEREBRONN (The Brain)"
echo "  Status: $(systemctl --user is-active cerebronn 2>/dev/null || echo 'unknown')"
echo "  Current: Maintaining briefing.md, Cycle #$(grep -o 'cycle [0-9]*' $LOG_DIR/cerebronn/memory/briefing.md 2>/dev/null | tail -1 || echo 'unknown')"
echo "  Working on: Architecture, strategic decisions"
echo "  Last update: $(stat -c %y $LOG_DIR/cerebronn/memory/briefing.md 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1 || echo 'unknown')"
echo "  Inbox: $(ls $LOG_DIR/cerebronn/inbox/ 2>/dev/null | wc -l) pending"
echo ""

# HELIOS
echo "🌐 HELIOS (The Spine)"
echo "  Status: $(systemctl --user is-active helios 2>/dev/null || echo 'unknown')"
echo "  Current: 15-min audits, dashboard sync"
echo "  Last sync: $(tail -1 $LOG_DIR/helios/helios.log 2>/dev/null | grep -o '[0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*' || echo 'unknown')"
echo "  Reports to me: Every 15 min"
echo "  Reports to you: See separate digest"
echo ""

# FORGER
echo "🔨 FORGER (The Builder)"
echo "  Status: $(systemctl --user is-active forger 2>/dev/null || echo 'unknown')"
FORGER_TASK=$(ls -1t $LOG_DIR/forger/inbox/TASK* 2>/dev/null | head -1)
if [ -n "$FORGER_TASK" ]; then
    echo "  Current task: $(basename $FORGER_TASK)"
    echo "  Working on: $(head -5 $FORGER_TASK 2>/dev/null | grep -o 'TASK:.*\|##.*' | head -1)"
fi
echo "  Inbox: $(ls $LOG_DIR/forger/inbox/ 2>/dev/null | wc -l) tasks pending"
echo "  Outbox: $(ls $LOG_DIR/forger/outbox/ 2>/dev/null | wc -l) completed"
echo "  Builds: $(ls $LOG_DIR/forger/builds/ 2>/dev/null | wc -l) projects"
echo ""

# QUANTA
echo "📊 QUANTA (The Trader)"
echo "  Status: $(systemctl --user is-active quanta-v3 2>/dev/null || echo 'STOPPED')"
echo "  Current: Trading halted (your command)"
echo "  Position: 0 active trades"
echo "  Note: Shut down due to losses"
echo ""

# CHAD_YI (Me)
echo "🎭 CHAD_YI (The Face - Me)"
echo "  Status: Active"
echo "  Inbox: $(ls $LOG_DIR/chad-yi/inbox/*.md 2>/dev/null | wc -l) messages"
echo "  Reports to you: 7x daily + on-demand"
echo ""

# Priority tasks
echo "🔴 PRIORITY TASKS"
grep -E "^\| 🔴\|^\| 🟡" /home/chad-yi/.openclaw/workspace/ACTIVE.md 2>/dev/null | head -3 || echo "  Check ACTIVE.md for details"
