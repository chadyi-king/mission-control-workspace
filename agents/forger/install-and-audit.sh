#!/bin/bash
# INSTALL + AUDIT - Installs skills with real-time security checks
# Run: ./install-and-audit.sh

set -e

SKILLS_DIR="/home/chad-yi/.openclaw/workspace/agents/forger/skills"
AUDIT_LOG="/home/chad-yi/.openclaw/workspace/agents/forger/install-audit.log"
DELAY=180  # 3 minutes between installs

cd "$SKILLS_DIR"

# Remaining skills to install (excluding already installed)
REMAINING_SKILLS=(
    "qwen-image"
    "antigravity-image-gen"
    "nano-banana-pro-openrouter"
    "vercel"
    "domain-dns-ops"
    "cloudflare-api"
    "google-ads"
    "google-analytics"
    "meta-ads"
    "stripe"
    "shopify-admin-api"
    "webflow-api"
)

echo "========================================" | tee -a "$AUDIT_LOG"
echo "INSTALL + AUDIT - Real-time Security" | tee -a "$AUDIT_LOG"
echo "Started: $(date)" | tee -a "$AUDIT_LOG"
echo "Skills to install: ${#REMAINING_SKILLS[@]}" | tee -a "$AUDIT_LOG"
echo "========================================" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

# Function to audit a single skill
audit_skill() {
    local skill_name=$1
    local skill_path="$SKILLS_DIR/$skill_name"
    
    echo "" | tee -a "$AUDIT_LOG"
    echo "🔍 AUDIT: $skill_name" | tee -a "$AUDIT_LOG"
    echo "----------------------------------------" | tee -a "$AUDIT_LOG"
    
    if [ ! -d "$skill_path" ]; then
        echo "❌ Skill directory not found" | tee -a "$AUDIT_LOG"
        return 1
    fi
    
    # Check 1: Origin
    if [ -f "$skill_path/.clawhub/origin.json" ]; then
        author=$(grep -o '"author":"[^"]*"' "$skill_path/.clawhub/origin.json" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
        echo "✅ Origin: $author" | tee -a "$AUDIT_LOG"
    else
        echo "⚠️  No origin metadata" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 2: Malicious patterns
    suspicious=$(find "$skill_path" -type f \( -name "*.sh" -o -name "*.py" \) -exec grep -l "rm -rf /\|curl.*|.*sh\|wget.*|.*sh\|eval.*\$" {} \; 2>/dev/null || true)
    if [ -n "$suspicious" ]; then
        echo "🚨 WARNING: Suspicious patterns in:" | tee -a "$AUDIT_LOG"
        echo "$suspicious" | tee -a "$AUDIT_LOG"
    else
        echo "✅ No malicious patterns" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 3: Secrets
    secrets=$(grep -r "password\|secret\|token\|key" "$skill_path" --include="*.py" --include="*.js" 2>/dev/null | grep -v "getenv\|process.env\|input(" | head -3 || true)
    if [ -n "$secrets" ]; then
        echo "⚠️  Potential hardcoded values:" | tee -a "$AUDIT_LOG"
        echo "$secrets" | tee -a "$AUDIT_LOG"
    else
        echo "✅ No hardcoded secrets" | tee -a "$AUDIT_LOG"
    fi
    
    # Check 4: File count
    file_count=$(find "$skill_path" -type f | wc -l)
    echo "ℹ️  Files: $file_count" | tee -a "$AUDIT_LOG"
    
    echo "✅ Audit complete for $skill_name" | tee -a "$AUDIT_LOG"
}

# Install and audit each skill
for skill in "${REMAINING_SKILLS[@]}"; do
    echo "" | tee -a "$AUDIT_LOG"
    echo "========================================" | tee -a "$AUDIT_LOG"
    echo "[$(date '+%H:%M:%S')] INSTALLING: $skill" | tee -a "$AUDIT_LOG"
    echo "========================================" | tee -a "$AUDIT_LOG"
    
    # Check if already exists
    if [ -d "$skill" ]; then
        echo "⚠️  $skill already exists - auditing only" | tee -a "$AUDIT_LOG"
        audit_skill "$skill"
        continue
    fi
    
    # Install
    if clawhub install "$skill" --dir . 2>> "$AUDIT_LOG"; then
        echo "✅ INSTALLED: $skill" | tee -a "$AUDIT_LOG"
        
        # Immediate audit
        audit_skill "$skill"
    else
        echo "❌ FAILED: $skill (may be rate limited)" | tee -a "$AUDIT_LOG"
        echo "⏳ Waiting extra 5 min..." | tee -a "$AUDIT_LOG"
        sleep 300
        
        # Retry once
        echo "🔄 Retrying $skill..." | tee -a "$AUDIT_LOG"
        if clawhub install "$skill" --dir . 2>> "$AUDIT_LOG"; then
            echo "✅ INSTALLED (retry): $skill" | tee -a "$AUDIT_LOG"
            audit_skill "$skill"
        else
            echo "❌ FAILED (retry): $skill - skipping" | tee -a "$AUDIT_LOG"
        fi
    fi
    
    # Delay before next
    echo "" | tee -a "$AUDIT_LOG"
    echo "⏳ Waiting $DELAY seconds..." | tee -a "$AUDIT_LOG"
    sleep $DELAY
done

echo "" | tee -a "$AUDIT_LOG"
echo "========================================" | tee -a "$AUDIT_LOG"
echo "INSTALL + AUDIT COMPLETE" | tee -a "$AUDIT_LOG"
echo "Finished: $(date)" | tee -a "$AUDIT_LOG"
echo "========================================" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"
echo "FINAL SKILL COUNT: $(ls -1 | wc -l)" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"
echo "All installed skills:" | tee -a "$AUDIT_LOG"
ls -1 | tee -a "$AUDIT_LOG"
