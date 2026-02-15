#!/bin/bash
# Install Agent Infrastructure
# Run this to set up the complete infrastructure

set -e

echo "=============================================="
echo "AGENT INFRASTRUCTURE INSTALLER"
echo "=============================================="
echo ""

BASE_DIR="/home/chad-yi/.openclaw/workspace"
INFRA_DIR="$BASE_DIR/infrastructure"

# Check if running from correct directory
if [ ! -d "$INFRA_DIR" ]; then
    echo "❌ Error: infrastructure/ directory not found"
    echo "   Run from: $BASE_DIR"
    exit 1
fi

echo "[1/6] Installing Python dependencies..."
pip3 install --user websockets flask requests 2>/dev/null || pip3 install websockets flask requests
echo "✅ Dependencies installed"
echo ""

echo "[2/6] Installing systemd services..."

# Agent Hub
cp "$INFRA_DIR/hub/agent-hub.service" ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable agent-hub
systemctl --user start agent-hub
echo "✅ Agent Hub installed (port 9000)"

# Tool Bridge
cp "$INFRA_DIR/tool-bridge/tool-bridge.service" ~/.config/systemd/user/
systemctl --user enable tool-bridge
systemctl --user start tool-bridge
echo "✅ Tool Bridge installed (port 9001)"

# Agent Supervisor
cp "$INFRA_DIR/supervisor/agent-supervisor.service" ~/.config/systemd/user/
systemctl --user enable agent-supervisor
systemctl --user start agent-supervisor
echo "✅ Agent Supervisor installed"

echo ""
echo "[3/6] Checking service status..."
sleep 2

# Check services
for svc in agent-hub tool-bridge agent-supervisor; do
    if systemctl --user is-active --quiet $svc; then
        echo "  ✅ $svc running"
    else
        echo "  ⚠️  $svc not running (check logs: journalctl --user -u $svc)"
    fi
done

echo ""
echo "[4/6] Creating API keys template..."
if [ ! -f "$INFRA_DIR/tool-bridge/api-keys.json" ]; then
    cat > "$INFRA_DIR/tool-bridge/api-keys.json" << 'EOF'
{
  "openai": null,
  "allowed_agents": [
    "forger",
    "helios", 
    "escritor",
    "quanta",
    "mensamusa",
    "autour",
    "chad_yi"
  ]
}
EOF
    echo "✅ API keys template created"
    echo "   EDIT: $INFRA_DIR/tool-bridge/api-keys.json"
    echo "   Add your OpenAI API key to enable image generation"
else
    echo "✅ API keys file already exists"
fi

echo ""
echo "[5/6] Testing connectivity..."
sleep 1

# Test hub
if lsof -i :9000 > /dev/null 2>&1; then
    echo "  ✅ WebSocket Hub (port 9000) reachable"
else
    echo "  ⚠️  WebSocket Hub not responding"
fi

# Test tool bridge
if curl -s http://localhost:9001/health > /dev/null 2>&1; then
    echo "  ✅ Tool Bridge (port 9001) reachable"
else
    echo "  ⚠️  Tool Bridge not responding"
fi

echo ""
echo "[6/6] Installing agent client library..."
chmod +x "$INFRA_DIR/agent-client.py"
echo "✅ Agent client library ready"

echo ""
echo "=============================================="
echo "INSTALLATION COMPLETE"
echo "=============================================="
echo ""
echo "Infrastructure Services:"
echo "  • WebSocket Hub:     ws://localhost:9000"
echo "  • Tool Bridge:       http://localhost:9001"
echo "  • Agent Supervisor:  Running every 30s"
echo ""
echo "Next Steps:"
echo "  1. Add OpenAI API key to enable image generation"
echo "     Edit: $INFRA_DIR/tool-bridge/api-keys.json"
echo ""
echo "  2. Update agents to use client library"
echo "     Import: from agent-client import AgentClient"
echo ""
echo "  3. Monitor with:"
echo "     journalctl --user -f -u agent-hub"
echo "     journalctl --user -f -u tool-bridge"
echo "     journalctl --user -f -u agent-supervisor"
echo ""
echo "  4. Test connectivity:"
echo "     python3 $INFRA_DIR/agent-client.py"
echo ""
echo "=============================================="
