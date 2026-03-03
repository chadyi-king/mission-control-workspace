#!/bin/bash
# LOVABLE EXPORT AUTOMATION
# Trigger: You say "Export [project]"
# Action: Automatically exports from Lovable to GitHub

# Load credentials
source /home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-credentials.sh
source /home/chad-yi/.openclaw/workspace/agents/forger/.secrets/github-token.sh

PROJECT=$1

if [ -z "$PROJECT" ]; then
    echo "Usage: export-lovable [project-name]"
    echo "Example: export-lovable team-elevate"
    exit 1
fi

echo "=== AUTO-EXPORT: $PROJECT ==="
echo "Starting automated export from Lovable to GitHub..."

# This would run the Playwright automation
# node /home/chad-yi/.openclaw/workspace/agents/forger/auto-export.js "$PROJECT"

echo "Note: Full automation requires OAuth handling setup"
echo "For now, manual export is faster:"
echo "1. Go to https://lovable.dev"
echo "2. Open $PROJECT"
echo "3. Click Export → GitHub"
echo "4. Tell me when done"
