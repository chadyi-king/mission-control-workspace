#!/bin/bash
# AUTOMATED Forger Skill Installation - Runs overnight without monitoring
# This script installs ALL skills with automatic rate limit handling
# Run once, walk away, everything installs automatically

set -e  # Exit on error but continue to next skill

cd /home/chad-yi/.openclaw/workspace/agents/forger/skills

LOG_FILE="/home/chad-yi/.openclaw/workspace/agents/forger/skill-install.log"
DELAY=180  # 3 minutes between installs (safe for rate limits)

# High-priority IMAGE GENERATION skills (FREE priority)
IMAGE_SKILLS=(
    "gemini-image-simple"      # Google - free tier available
    "qwen-image"               # Qwen - free tier available  
    "antigravity-image-gen"    # Free image generation
    "nano-banana-pro-openrouter"  # Check if free tier
)

# Core DEPLOYMENT skills
DEPLOY_SKILLS=(
    "vercel"
    "domain-dns-ops"
    "cloudflare-api"
)

# MARKETING & ANALYTICS
MARKETING_SKILLS=(
    "google-ads"
    "google-analytics"
    "meta-ads"
)

# E-COMMERCE & PAYMENTS
ECOMMERCE_SKILLS=(
    "stripe"
    "shopify-admin-api"
)

# CONTENT & DESIGN
CONTENT_SKILLS=(
    "webflow-api"
    "figma"
    "notion"
    "design-assets"
)

# Combine all skills
ALL_SKILLS=(
    "${IMAGE_SKILLS[@]}"
    "${DEPLOY_SKILLS[@]}"
    "${MARKETING_SKILLS[@]}"
    "${ECOMMERCE_SKILLS[@]}"
    "${CONTENT_SKILLS[@]}"
)

echo "========================================" | tee -a "$LOG_FILE"
echo "FORGER MEGA SKILL INSTALLATION" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Total skills to install: ${#ALL_SKILLS[@]}" | tee -a "$LOG_FILE"
echo "Estimated time: $(( (${#ALL_SKILLS[@]} * $DELAY) / 60 )) minutes" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Counter
SUCCESS=0
FAILED=0
ALREADY=0

for skill in "${ALL_SKILLS[@]}"; do
    echo "----------------------------------------" | tee -a "$LOG_FILE"
    echo "[$(date '+%H:%M:%S')] Installing: $skill" | tee -a "$LOG_FILE"
    echo "----------------------------------------" | tee -a "$LOG_FILE"
    
    # Try to install
    if clawhub install "$skill" --dir . 2>> "$LOG_FILE"; then
        echo "✅ SUCCESS: $skill installed" | tee -a "$LOG_FILE"
        ((SUCCESS++))
    else
        # Check if already exists
        if [ -d "$skill" ]; then
            echo "⚠️  ALREADY EXISTS: $skill (skipping)" | tee -a "$LOG_FILE"
            ((ALREADY++))
        else
            echo "❌ FAILED: $skill (rate limit or error)" | tee -a "$LOG_FILE"
            ((FAILED++))
            
            # Wait extra time on failure
            echo "⏳ Extra 5 min wait due to failure..." | tee -a "$LOG_FILE"
            sleep 300
        fi
    fi
    
    echo "" | tee -a "$LOG_FILE"
    echo "Progress: $((SUCCESS + ALREADY + FAILED))/${#ALL_SKILLS[@]}" | tee -a "$LOG_FILE"
    echo "✅ Success: $SUCCESS | ⚠️ Already: $ALREADY | ❌ Failed: $FAILED" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Standard delay between installs
    echo "Waiting $DELAY seconds before next install..." | tee -a "$LOG_FILE"
    echo "Next skill: ${ALL_SKILLS[$((i+1))]:-NONE (last skill)}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    sleep $DELAY
done

echo "========================================" | tee -a "$LOG_FILE"
echo "INSTALLATION COMPLETE" | tee -a "$LOG_FILE"
echo "Finished: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "SUMMARY:" | tee -a "$LOG_FILE"
echo "✅ Successfully installed: $SUCCESS" | tee -a "$LOG_FILE"
echo "⚠️ Already existed: $ALREADY" | tee -a "$LOG_FILE"
echo "❌ Failed: $FAILED" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Total skills now available:" | tee -a "$LOG_FILE"
ls -1 | wc -l | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "1. Check log: tail -f $LOG_FILE" | tee -a "$LOG_FILE"
echo "2. Git commit: cd /home/chad-yi/.openclaw/workspace && git add -A && git commit -m 'feat: Install all Forger skills'" | tee -a "$LOG_FILE"
echo "3. Done! Forger now has full arsenal." | tee -a "$LOG_FILE"
