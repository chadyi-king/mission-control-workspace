#!/bin/bash
# setup_telegram_bot.sh — Configure Tele (Telegram Main Agent)
# Run this after creating bot via @BotFather

set -e

TELE_DIR="/home/chad-yi/.openclaw/workspace/agents/tele"
STATE_FILE="$TELE_DIR/state.json"

echo "=== Tele (Telegram Main Agent) Setup ==="
echo ""

# Check if bot token is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup_telegram_bot.sh <BOT_TOKEN>"
    echo ""
    echo "Get your bot token from @BotFather on Telegram:"
    echo "1. Message @BotFather"
    echo "2. Type /newbot"
    echo "3. Follow instructions"
    echo "4. Copy the token and run:"
    echo "   ./setup_telegram_bot.sh YOUR_TOKEN_HERE"
    exit 1
fi

BOT_TOKEN="$1"

echo "🔑 Setting up bot with provided token..."

# Test the token
echo "🧪 Testing token..."
TEST_RESPONSE=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")

if echo "$TEST_RESPONSE" | grep -q '"ok":true'; then
    BOT_USERNAME=$(echo "$TEST_RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Token valid! Bot: @${BOT_USERNAME}"
else
    echo "❌ Token invalid or API error"
    echo "Response: $TEST_RESPONSE"
    exit 1
fi

# Update state.json
echo "📝 Updating agent state..."
cat > "$STATE_FILE" << EOF
{
  "agent": "tele",
  "status": "active",
  "created": "2026-02-28T08:16:00Z",
  "last_active": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "telegram": {
    "bot_username": "${BOT_USERNAME}",
    "bot_token_set": true,
    "webhook_url": null,
    "polling_active": false,
    "chat_id": null
  },
  "stats": {
    "messages_received": 0,
    "messages_sent": 0,
    "commands_processed": 0,
    "errors": 0
  },
  "version": "1.0.0"
}
EOF

echo "✅ State updated"

# Set bot commands via API
echo "📋 Setting bot commands..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyCommands" \
    -H "Content-Type: application/json" \
    -d '[
        {"command":"start","description":"Welcome message and capabilities overview"},
        {"command":"status","description":"Quick dashboard status summary"},
        {"command":"tasks","description":"List active and pending tasks"},
        {"command":"agents","description":"Show agent status overview"},
        {"command":"help","description":"Command reference and usage"},
        {"command":"heartbeat","description":"Manual heartbeat and system check"}
    ]' > /dev/null

echo "✅ Commands set"

# Save token to environment file
ENV_FILE="$TELE_DIR/.env"
echo "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}" > "$ENV_FILE"
chmod 600 "$ENV_FILE"
echo "✅ Token saved to .env (restricted permissions)"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Bot: @${BOT_USERNAME}"
echo "Status: Ready for activation"
echo ""
echo "Next steps:"
echo "1. Message your bot on Telegram: @${BOT_USERNAME}"
echo "2. Type /start to verify connectivity"
echo "3. Configure webhook or polling in OpenClaw"
echo ""
echo "Environment file: $ENV_FILE"
echo "Agent state: $STATE_FILE"
