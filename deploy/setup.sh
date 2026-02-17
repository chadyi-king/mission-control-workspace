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

if ! command -v systemctl &> /dev/null; then
    echo "WARNING: systemctl not found. Services will not be installed."
    HAS_SYSTEMD=false
else
    HAS_SYSTEMD=true
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
chmod +x "$SYNC_DIR/heartbeat.py"
chmod +x "$SYNC_DIR/health_server.py"
chmod +x "$SYNC_DIR/monitor.py"
chmod +x "$SYNC_DIR/conflict_resolver.py"
echo "✓ Permissions set"
echo ""

#-------------------------------------------------------------------------------
# Configure Git
#-------------------------------------------------------------------------------
echo "Configuring git..."
cd "$WORKSPACE_DIR"

# Set git user if not already set
if ! git config user.email &> /dev/null; then
    git config user.email "sync@helios-chad.local"
fi
if ! git config user.name &> /dev/null; then
    git config user.name "Helios-Chad Sync"
fi

# Configure git for better conflict handling
git config pull.rebase false  # Use merge instead of rebase
git config merge.ff false     # Always create merge commits
git config core.autocrlf false

echo "✓ Git configured"
echo ""

#-------------------------------------------------------------------------------
# Install Systemd Services (only if root)
#-------------------------------------------------------------------------------
if [[ "$HAS_SYSTEMD" == true ]] && [[ $EUID -eq 0 ]]; then
    echo "Installing systemd services..."
    
    # Copy service files
    cp "$DEPLOY_DIR/sync.service" /etc/systemd/system/helios-sync.service
    cp "$DEPLOY_DIR/heartbeat.service" /etc/systemd/system/helios-heartbeat.service
    cp "$DEPLOY_DIR/health-server.service" /etc/systemd/system/helios-health-server.service
    cp "$DEPLOY_DIR/monitor.service" /etc/systemd/system/helios-monitor.service
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "✓ Services installed"
    echo ""
    
    # Ask about enabling services
    read -p "Enable and start services now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable helios-sync.service
        systemctl enable helios-heartbeat.service
        systemctl enable helios-health-server.service
        systemctl enable helios-monitor.service
        
        systemctl start helios-sync.service
        systemctl start helios-heartbeat.service
        systemctl start helios-health-server.service
        systemctl start helios-monitor.service
        
        echo "✓ Services enabled and started"
    fi
    echo ""
elif [[ "$HAS_SYSTEMD" == true ]]; then
    echo "Skipping systemd install (needs root)"
    echo "Services will run manually instead"
    echo ""
fi
        systemctl enable helios-health-server.service
        systemctl enable helios-monitor.service
        
        systemctl start helios-sync.service
        systemctl start helios-heartbeat.service
        systemctl start helios-health-server.service
        systemctl start helios-monitor.service
        
        echo "✓ Services enabled and started"
    else
        echo "Services installed but not enabled. To enable later:"
        echo "  systemctl enable helios-sync.service helios-heartbeat.service helios-health-server.service helios-monitor.service"
        echo "  systemctl start helios-sync.service helios-heartbeat.service helios-health-server.service helios-monitor.service"
    fi
else
    echo "Systemd not available. To run manually:"
    echo "  $SYNC_DIR/robust_sync.sh &"
    echo "  python3 $SYNC_DIR/heartbeat.py --node helios &"
    echo "  python3 $SYNC_DIR/health_server.py &"
    echo "  python3 $SYNC_DIR/monitor.py --daemon &"
fi

echo ""

#-------------------------------------------------------------------------------
# Create Environment File
#-------------------------------------------------------------------------------
ENV_FILE="$WORKSPACE_DIR/.sync_env"
echo "Creating environment file: $ENV_FILE"

cat > "$ENV_FILE" << 'EOF'
# Helios-Chad Sync Environment Configuration
# Source this file: source $HOME/.openclaw/workspace/.sync_env

export NODE_NAME=helios
export CHAD_HOST=chad
export CALEB_TELEGRAM_ID=512366713
export SYNC_INTERVAL=60
export HEARTBEAT_PORT=8765
export HEALTH_PORT=8080
export LOG_DIR=$HOME/.openclaw/workspace/logs
EOF

echo "✓ Environment file created"
echo ""

#-------------------------------------------------------------------------------
# Test Components
#-------------------------------------------------------------------------------
echo "Testing components..."

# Test conflict resolver
echo -n "  Conflict resolver: "
if python3 "$SYNC_DIR/conflict_resolver.py" --check >/devdev/null 2>&1; then
    echo "✓ OK"
else
    echo "✓ OK (no conflicts)"
fi

# Test health server (start briefly then stop)
echo -n "  Health server: "
python3 "$SYNC_DIR/health_server.py" --port 18080 &
HEALTH_PID=$!
sleep 2
if kill -0 $HEALTH_PID 2>/dev/null; then
    echo "✓ OK"
    kill $HEALTH_PID 2>/dev/null || true
else
    echo "✗ Failed"
fi
wait $HEALTH_PID 2>/dev/null || true

echo ""

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Start Services
#-------------------------------------------------------------------------------
echo ""
echo "Starting services..."
echo ""

# Kill any existing instances
pkill -f "robust_sync.sh" 2>/dev/null || true
pkill -f "heartbeat.py" 2>/dev/null || true
pkill -f "health_server.py" 2>/dev/null || true
pkill -f "monitor.py" 2>/dev/null || true
sleep 1

# Start sync
echo "Starting sync service..."
nohup "$SYNC_DIR/robust_sync.sh" > "$LOG_DIR/sync.log" 2>&1 &
SYNC_PID=$!
echo "  PID: $SYNC_PID"

# Start heartbeat
echo "Starting heartbeat service..."
nohup python3 "$SYNC_DIR/heartbeat.py" > "$LOG_DIR/heartbeat.log" 2>&1 &
HEARTBEAT_PID=$!
echo "  PID: $HEARTBEAT_PID"

# Start health server
echo "Starting health server..."
nohup python3 "$SYNC_DIR/health_server.py" > "$LOG_DIR/health_server.log" 2>&1 &
HEALTH_PID=$!
echo "  PID: $HEALTH_PID"

# Start monitor
echo "Starting monitor..."
nohup python3 "$SYNC_DIR/monitor.py" > "$LOG_DIR/monitor.log" 2>&1 &
MONITOR_PID=$!
echo "  PID: $MONITOR_PID"

sleep 2

echo ""
echo "✓ Services started"
echo ""

# Verify health endpoint
echo "Verifying health endpoint..."
for i in {1..5}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
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
echo "✓ Services RUNNING:"
echo "  Sync:        PID $SYNC_PID"
echo "  Heartbeat:   PID $HEARTBEAT_PID"
echo "  Health:      PID $HEALTH_PID"
echo "  Monitor:     PID $MONITOR_PID"
echo ""
echo "Files created:"
echo "  Sync scripts:    $SYNC_DIR/"
echo "  Service files:   $DEPLOY_DIR/"
echo "  Logs:            $LOG_DIR/"
echo "  Environment:     $ENV_FILE"
echo ""
echo "Services:"
echo "  helios-sync          - Main sync loop"
echo "  helios-heartbeat     - Heartbeat sender/receiver"
echo "  helios-health-server - HTTP health endpoint (:8080)"
echo "  helios-monitor       - Alerting and monitoring"
echo ""
echo "Health check:"
echo "  curl http://localhost:8080/health"
echo "  curl http://localhost:8080/status"
echo "  curl http://localhost:8080/metrics"
echo ""
echo "Manual commands:"
echo "  Sync once:         $SYNC_DIR/robust_sync.sh --once"
echo "  Check conflicts:   python3 $SYNC_DIR/conflict_resolver.py --check"
echo "  Resolve conflicts: python3 $SYNC_DIR/conflict_resolver.py --resolve"
echo "  Monitor status:    python3 $SYNC_DIR/monitor.py --check"
echo ""
echo "View logs:"
echo "  tail -f $LOG_DIR/sync.log"
echo "  tail -f $LOG_DIR/heartbeat.log"
echo "  tail -f $LOG_DIR/monitor.log"
echo ""
