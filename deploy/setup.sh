#!/bin/bash
#===============================================================================
# Setup Script for Helios-Chad Robust Sync System
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/home/chad-yi/.openclaw/workspace"
SYNC_DIR="$WORKSPACE_DIR/sync"
DEPLOY_DIR="$WORKSPACE_DIR/deploy"
LOG_DIR="$WORKSPACE_DIR/logs"

echo "==================================="
echo "Helios-Chad Sync System Setup"
echo "==================================="
echo ""

#-------------------------------------------------------------------------------
# Check Prerequisites
#-------------------------------------------------------------------------------
echo "Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "ERROR: git is not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

#-------------------------------------------------------------------------------
# Create Directories
#-------------------------------------------------------------------------------
echo "Creating directories..."
mkdir -p "$SYNC_DIR" "$LOG_DIR" "$SYNC_DIR/conflicts" "$SYNC_DIR/backups" "$SYNC_DIR/pending"
echo "✓ Directories created"
echo ""

#-------------------------------------------------------------------------------
# Set Permissions
#-------------------------------------------------------------------------------
echo "Setting permissions..."
chmod +x "$SYNC_DIR/robust_sync.sh"
chmod +x "$SYNC_DIR/"*.py
echo "✓ Permissions set"
echo ""

#-------------------------------------------------------------------------------
# Configure Git
#-------------------------------------------------------------------------------
echo "Configuring git..."
cd "$WORKSPACE_DIR"

if ! git config user.email &> /dev/null; then
    git config user.email "sync@helios-chad.local"
fi
if ! git config user.name &> /dev/null; then
    git config user.name "Helios-Chad Sync"
fi

git config pull.rebase false
git config merge.ff false
git config core.autocrlf false

echo "✓ Git configured"
echo ""

#-------------------------------------------------------------------------------
# Create Environment File
#-------------------------------------------------------------------------------
ENV_FILE="$WORKSPACE_DIR/.sync_env"
echo "Creating environment file..."

cat > "$ENV_FILE" << EOF
# Helios-Chad Sync Environment
export NODE_NAME=chad
export SYNC_INTERVAL=30
export HEALTH_PORT=8080
export LOG_DIR=$LOG_DIR
EOF

echo "✓ Environment file created"
echo ""

#-------------------------------------------------------------------------------
# Start Services
#-------------------------------------------------------------------------------
echo "Starting services..."
echo ""

# Kill any existing
pkill -f "robust_sync.sh" 2>/dev/null || true
pkill -f "health_server.py" 2>/dev/null || true
pkill -f "heartbeat.py" 2>/dev/null || true
pkill -f "monitor.py" 2>/dev/null || true
sleep 1

# Start sync
echo "  Starting sync..."
nohup "$SYNC_DIR/robust_sync.sh" > "$LOG_DIR/sync.log" 2>&1 &
echo "    PID: $!"

# Start health server
echo "  Starting health server..."
nohup python3 "$SYNC_DIR/health_server.py" > "$LOG_DIR/health.log" 2>&1 &
echo "    PID: $!"

# Start heartbeat
echo "  Starting heartbeat..."
nohup python3 "$SYNC_DIR/heartbeat.py" > "$LOG_DIR/heartbeat.log" 2>&1 &
echo "    PID: $!"

# Start monitor
echo "  Starting monitor..."
nohup python3 "$SYNC_DIR/monitor.py" > "$LOG_DIR/monitor.log" 2>&1 &
echo "    PID: $!"

sleep 2

echo ""
echo "✓ Services started"
echo ""

#-------------------------------------------------------------------------------
# Verify
#-------------------------------------------------------------------------------
echo "Verifying health endpoint..."
for i in {1..5}; do
    if curl -s http://localhost:8080/health 2>/dev/null | grep -q "ok"; then
        echo "✓ Health server responding"
        break
    fi
    sleep 1
done

echo ""

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Services RUNNING:"
echo "  Sync:      $SYNC_DIR/robust_sync.sh"
echo "  Health:    http://localhost:8080/health"
echo "  Logs:      $LOG_DIR/"
echo ""
echo "Check status:"
echo "  curl http://localhost:8080/health"
echo "  curl http://localhost:8080/status"
echo ""
echo "View logs:"
echo "  tail -f $LOG_DIR/sync.log"
echo "  tail -f $LOG_DIR/health.log"
echo ""
echo "✓ READY for autonomous coordination!"
echo ""
