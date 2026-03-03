#!/bin/bash
# Install ALL Forger skills with proper delays
# Run this and it will install everything with automatic rate limit handling

cd /home/chad-yi/.openclaw/workspace/agents/forger/skills

SKILLS=(
    "vercel"
    "domain-dns-ops"
    "cloudflare-api"
    "google-drive"
    "nano-banana-pro-openrouter"
    "google-ads"
    "google-analytics"
    "stripe"
    "meta-ads"
    "shopify-admin-api"
    "webflow-api"
    "figma"
    "notion"
)

DELAY_BETWEEN=180  # 3 minutes between installs

echo "=== FORGER MEGA SKILL INSTALLATION ==="
echo "Installing $(echo ${#SKILLS[@]}) skills with $DELAY_BETWEEN second delays"
echo ""
echo "Already installed:"
ls -1
echo ""

for skill in "${SKILLS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Installing: $skill"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Try to install
    clawhub install "$skill" --dir .
    
    if [ $? -eq 0 ]; then
        echo "✅ $skill installed successfully"
    else
        echo "⚠️  Issue with $skill - may be rate limited or already exists"
    fi
    
    echo ""
    echo "Waiting $DELAY_BETWEEN seconds before next install..."
    echo "$(date '+%H:%M:%S') - Next: ${SKILLS[$((i+1))]}"
    sleep $DELAY_BETWEEN
done

echo ""
echo "=== INSTALLATION COMPLETE ==="
echo "Installed skills:"
ls -1 | wc -l
echo ""
echo "Skills:"
ls -1
echo ""
echo "Run: git add . && git commit -m 'feat: Install all Forger skills'"
