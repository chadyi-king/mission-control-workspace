#!/bin/bash
# Morning Report Generator
# Run this in the morning to see what happened overnight

cd /home/chad-yi/.openclaw/workspace

echo "=================================="
echo "MORNING REPORT - Mission Control"
echo "=================================="
echo ""

# 1. Check Helios audits
echo "📊 HELIOS AUDITS (Last 5):"
ls -lt agents/helios/outbox/audit-*.json 2>/dev/null | head -5 | awk '{print $6, $7, $8, $9}'
echo ""

# 2. Check Quanta activity
echo "📈 QUANTA ACTIVITY:"
if [ -f agents/quanta/logs/all_messages.jsonl ]; then
    echo "  Messages logged: $(wc -l < agents/quanta/logs/all_messages.jsonl)"
    echo "  Last 24h signals: $(grep 'signal' agents/quanta/logs/all_messages.jsonl 2>/dev/null | wc -l)"
fi
echo ""

# 3. Check data integrity
echo "💾 DATA STATUS:"
python3 scripts/verify-data.py 2>/dev/null | grep -E "Tasks:|passed"
echo ""

# 4. Check git status
echo "📝 RECENT COMMITS:"
git log --oneline -3 2>/dev/null
echo ""

# 5. System status
echo "🔧 SERVICE STATUS:"
echo "  Helios: $(systemctl is-active helios 2>/dev/null || echo 'unknown')"
echo "  Quanta: $(systemctl is-active quanta 2>/dev/null || echo 'not installed')"
echo ""

echo "=================================="
