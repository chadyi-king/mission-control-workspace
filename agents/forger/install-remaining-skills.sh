#!/bin/bash
# Install remaining Forger skills with automatic rate limit handling
# Run this script to complete Forger skill installation

cd /home/chad-yi/.openclaw/workspace/agents/forger/skills

echo "=== Forger Skill Installation ==="
echo "Already installed:"
ls -1
echo ""
echo "Installing remaining skills with rate limit handling..."
echo ""

SKILLS=("vercel" "domain-dns-ops" "cloudflare-api")

for skill in "${SKILLS[@]}"; do
    echo "Installing $skill..."
    clawhub install "$skill" --dir .
    if [ $? -eq 0 ]; then
        echo "✅ $skill installed"
    else
        echo "⏳ Rate limited. Waiting 5 minutes..."
        sleep 300
        echo "Retrying $skill..."
        clawhub install "$skill" --dir .
        if [ $? -eq 0 ]; then
            echo "✅ $skill installed"
        else
            echo "❌ $skill failed. Run script again later."
        fi
    fi
    echo ""
done

echo "=== Installation Complete ==="
echo "Installed skills:"
ls -1
echo ""
echo "Run: git add . && git commit -m 'feat: Install remaining Forger skills'"
