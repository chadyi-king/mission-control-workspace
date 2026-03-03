#!/bin/bash
# LOVABLE LOGIN AUTOMATION
# Secure credential setup for Lovable access

SKILL_DIR="/home/chad-yi/.openclaw/workspace/skills/agent-browser-stagehand"
ENV_FILE="$SKILL_DIR/.env"

echo "=== LOVABLE BROWSER AUTOMATION SETUP ==="
echo ""
echo "This will store your Lovable credentials securely."
echo ""

# Check if skill is set up
if [ ! -d "$SKILL_DIR/node_modules" ]; then
    echo "Setting up browser skill..."
    cd "$SKILL_DIR"
    npm install 2>/dev/null || echo "npm install may need manual run"
    npm link 2>/dev/null || echo "npm link may need manual run"
fi

# Create .env file
cat > "$ENV_FILE" << 'EOF'
# Lovable Credentials
LOVABLE_EMAIL=
LOVABLE_PASSWORD=

# Optional: Browserbase for better reliability
# BROWSERBASE_API_KEY=
# BROWSERBASE_PROJECT_ID=
EOF

echo "✅ Created .env file at: $ENV_FILE"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano $ENV_FILE"
echo ""
echo "2. Test login:"
echo "   cd $SKILL_DIR"
echo "   browser navigate https://lovable.dev"
echo ""
echo "Credentials are stored locally only (not in git)."
