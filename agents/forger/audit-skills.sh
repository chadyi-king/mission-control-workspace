#!/bin/bash
# SKILL SECURITY AUDIT - Run after skill installation
# Verifies skills are safe, checks for malicious code, validates origins

SKILLS_DIR="/home/chad-yi/.openclaw/workspace/agents/forger/skills"
AUDIT_LOG="/home/chad-yi/.openclaw/workspace/agents/forger/skill-audit.log"

echo "========================================" | tee -a "$AUDIT_LOG"
echo "SKILL SECURITY AUDIT" | tee -a "$AUDIT_LOG"
echo "Date: $(date)" | tee -a "$AUDIT_LOG"
echo "========================================" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

SAFE_COUNT=0
WARNING_COUNT=0
DANGER_COUNT=0

cd "$SKILLS_DIR" || exit 1

for skill in */; do
    skill_name=$(basename "$skill")
    echo "----------------------------------------" | tee -a "$AUDIT_LOG"
    echo "Auditing: $skill_name" | tee -a "$AUDIT_LOG"
    echo "----------------------------------------" | tee -a "$AUDIT_LOG"
    
    # Check 1: Origin verification
    if [ -f "$skill/.clawhub/origin.json" ]; then
        origin=$(cat "$skill/.clawhub/origin.json" 2>/dev/null | grep -o '"author":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Origin: $origin" | tee -a "$AUDIT_LOG"
    else
        echo "⚠️  No origin metadata found" | tee -a "$AUDIT_LOG"
        ((WARNING_COUNT++))
    fi
    
    # Check 2: No malicious scripts
    if find "$skill" -name "*.sh" -o -name "*.py" 2>/dev/null | xargs grep -l "rm -rf /\|curl.*|.*sh\|wget.*|.*sh" 2>/dev/null; then
        echo "🚨 DANGER: Suspicious commands found!" | tee -a "$AUDIT_LOG"
        ((DANGER_COUNT++))
    else
        echo "✅ No malicious patterns found" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 3: Network requests (expected for API skills)
    if grep -r "http" "$skill"/*.py "$skill"/*.js 2>/dev/null | grep -v "localhost\|127.0.0.1" | head -5; then
        echo "ℹ️  Makes external API calls (expected)" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 4: No hardcoded secrets
    if grep -r "password\|secret\|token\|key" "$skill"/*.py "$skill"/*.js 2>/dev/null | grep -v "PASSWORD\|getenv\|input("; then
        echo "⚠️  Potential hardcoded credentials" | tee -a "$AUDIT_LOG"
        ((WARNING_COUNT++))
    else
        echo "✅ No hardcoded secrets" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 5: File permissions
    if find "$skill" -type f -perm /o+w 2>/dev/null | head -1; then
        echo "⚠️  World-writable files found" | tee -a "$AUDIT_LOG"
        ((WARNING_COUNT++))
    else
        echo "✅ Permissions OK" | tee -a "$AUDIT_LOG"
    fi
    
    ((SAFE_COUNT++))
    echo "" | tee -a "$AUDIT_LOG"
done

echo "========================================" | tee -a "$AUDIT_LOG"
echo "AUDIT COMPLETE" | tee -a "$AUDIT_LOG"
echo "========================================" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"
echo "SUMMARY:" | tee -a "$AUDIT_LOG"
echo "✅ Safe: $SAFE_COUNT" | tee -a "$AUDIT_LOG"
echo "⚠️  Warnings: $WARNING_COUNT" | tee -a "$AUDIT_LOG"
echo "🚨 Dangers: $DANGER_COUNT" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

if [ $DANGER_COUNT -gt 0 ]; then
    echo "⚠️  SECURITY ISSUES FOUND - Review required!" | tee -a "$AUDIT_LOG"
    exit 1
else
    echo "✅ All skills passed basic security audit" | tee -a "$AUDIT_LOG"
    exit 0
fi
