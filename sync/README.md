# Helios-Chad Robust Sync System

A production-ready, crash-proof auto-sync system with monitoring, heartbeats, and automatic conflict resolution.

## Overview

This system ensures reliable synchronization between Helios and Chad with:
- **Self-healing scripts** - Auto-restart on crash
- **Heartbeat monitoring** - Detect when peers go down
- **Automatic conflict resolution** - Never lose messages
- **Health endpoints** - HTTP status for monitoring
- **Alert system** - Notify Caleb of issues

## Architecture

```
┌─────────┐     Heartbeat      ┌─────────┐
│ Helios  │ ◄────────────────► │  Chad   │
│ (you)   │                    │ (peer)  │
└────┬────┘                    └────┬────┘
     │                              │
     │  Git Sync (every 60s)        │
     └──────────┬───────────────────┘
                │
         ┌──────▼──────┐
         │  Conflict   │
         │  Resolver   │
         └──────┬──────┘
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Monitor│ │ Health │ │ Alerts │
│ (logs) │ │ Server │ │(Telegram)│
└────────┘ └────────┘ └────────┘
```

## Quick Start

### 1. Setup

```bash
cd /root/.openclaw/workspace
bash deploy/setup.sh
```

This will:
- Create necessary directories
- Set permissions
- Configure git
- Install systemd services
- Test components

### 2. Start Services

```bash
# If not auto-started during setup:
systemctl start helios-sync helios-heartbeat helios-health-server helios-monitor

# Enable auto-start on boot:
systemctl enable helios-sync helios-heartbeat helios-health-server helios-monitor
```

### 3. Verify

```bash
# Check service status
systemctl status helios-sync helios-heartbeat helios-health-server helios-monitor

# Check health endpoint
curl http://localhost:8080/health
curl http://localhost:8080/status

# View logs
tail -f logs/sync.log
tail -f logs/heartbeat.log
tail -f logs/monitor.log
```

## Components

### 1. Robust Sync (`sync/robust_sync.sh`)

Main sync loop with crash protection:
- Runs every 60 seconds
- Pulls before pushing (prevents conflicts)
- Auto-restarts on crash
- Prevents duplicate instances
- Alerts on repeated failures

**Commands:**
```bash
# Run continuously (default)
./sync/robust_sync.sh

# Run once
./sync/robust_sync.sh --once

# Stop gracefully
./sync/robust_sync.sh --stop

# Check status
./sync/robust_sync.sh --status
```

### 2. Heartbeat (`sync/heartbeat.py`)

UDP heartbeat system for peer monitoring:
- Sends heartbeat every 60 seconds
- Listens for peer heartbeats
- Tracks peer health status

**Commands:**
```bash
# Start heartbeat (Helios)
python3 sync/heartbeat.py --node helios --peer-host chad

# Start heartbeat (Chad)
python3 sync/heartbeat.py --node chad --peer-host helios
```

### 3. Health Server (`sync/health_server.py`)

HTTP endpoints for monitoring:
- `GET /health` - Basic health status
- `GET /status` - Detailed status
- `GET /metrics` - Prometheus-compatible metrics

**Example response:**
```json
{
  "status": "ok",
  "node": "helios",
  "last_sync": "2026-02-18T02:00:00Z",
  "messages_pending": 0,
  "uptime": 7200,
  "timestamp": "2026-02-18T02:00:00Z"
}
```

### 4. Monitor (`sync/monitor.py`)

Continuous monitoring with alerts:
- Checks heartbeat status
- Monitors sync health
- Detects git conflicts
- Alerts Caleb on issues

**Commands:**
```bash
# Run as daemon
python3 sync/monitor.py --daemon

# Run checks once
python3 sync/monitor.py --check
```

### 5. Conflict Resolver (`sync/conflict_resolver.py`)

Automatic git conflict resolution:
- Keeps both versions with timestamps
- Merges JSON files intelligently
- Never loses messages

**Commands:**
```bash
# Check for conflicts
python3 sync/conflict_resolver.py --check

# Resolve all conflicts
python3 sync/conflict_resolver.py --resolve

# Generate report
python3 sync/conflict_resolver.py --report

# Abort merge
python3 sync/conflict_resolver.py --abort
```

## Configuration

### Environment Variables

Create `.sync_env` in workspace root:

```bash
export NODE_NAME=helios          # or 'chad'
export CHAD_HOST=chad            # Peer hostname/IP
export CALEB_TELEGRAM_ID=512366713
export SYNC_INTERVAL=60
export HEARTBEAT_PORT=8765
export HEALTH_PORT=8080
```

Source it: `source /root/.openclaw/workspace/.sync_env`

### Systemd Services

Service files are in `deploy/`:
- `sync.service` - Main sync
- `heartbeat.service` - Heartbeat
- `health-server.service` - Health endpoint
- `monitor.service` - Monitoring

Edit and reload:
```bash
systemctl edit --full helios-sync
systemctl daemon-reload
systemctl restart helios-sync
```

## Monitoring

### Health Endpoints

```bash
# Basic health
curl http://localhost:8080/health

# Detailed status
curl http://localhost:8080/status

# Prometheus metrics
curl http://localhost:8080/metrics
```

### Logs

All logs are in `logs/`:
- `sync.log` - Sync operations
- `heartbeat.log` - Heartbeats
- `monitor.log` - Monitoring
- `conflict_resolver.log` - Conflict resolution
- `*_service.log` - Service output

### State Files

State is tracked in `sync/`:
- `sync_state.json` - Last sync info
- `heartbeat_state.json` - Local heartbeat
- `peer_*_state.json` - Peer heartbeats
- `monitor_status.json` - Monitor status

## Alerts

The system alerts Caleb via Telegram when:
- No heartbeat for 3+ minutes
- Sync fails 3 times in a row
- Git conflicts unresolved
- Process dies

Alerts respect a 5-minute cooldown to prevent spam.

## Testing Scenarios

### 1. Script Crash → Auto-restart

```bash
# Kill the sync process
pkill -f robust_sync.sh

# Check it restarts
systemctl status helios-sync
```

### 2. Network Down → Retry with Backoff

```bash
# Simulate network failure
iptables -A OUTPUT -p tcp --dport 22 -j DROP

# Check logs for retry attempts
tail -f logs/sync.log

# Restore network
iptables -D OUTPUT -p tcp --dport 22 -j DROP
```

### 3. Git Conflict → Auto-resolve

```bash
# Create a test conflict
echo '{"test": "local"}' > test_conflict.json
git add test_conflict.json
git commit -m "Local change"

# Simulate remote change
git fetch origin
git checkout origin/main -- test_conflict.json || true

# Run conflict resolver
python3 sync/conflict_resolver.py --resolve

# Check both versions saved
ls sync/conflicts/
```

### 4. Memory Check → Restart if Needed

```bash
# Monitor memory usage
ps -o pid,rss,comm -p $(pgrep -f robust_sync.sh)

# If memory > 500MB, process auto-restarts
```

## Troubleshooting

### Sync not running

```bash
# Check service status
systemctl status helios-sync

# Check for errors
journalctl -u helios-sync -n 50

# Try manual run
./sync/robust_sync.sh --once
```

### Heartbeat issues

```bash
# Check if port is in use
ss -uln | grep 8765

# Restart heartbeat
systemctl restart helios-heartbeat

# Check peer state
cat sync/peer_chad_state.json
```

### Health endpoint not responding

```bash
# Check if port is bound
ss -tln | grep 8080

# Test locally
curl http://localhost:8080/health

# Restart service
systemctl restart helios-health-server
```

### Conflicts not resolving

```bash
# Check conflict status
python3 sync/conflict_resolver.py --report

# Manual resolution
python3 sync/conflict_resolver.py --resolve

# If stuck, abort and retry
python3 sync/conflict_resolver.py --abort
```

## File Structure

```
/root/.openclaw/workspace/
├── sync/
│   ├── robust_sync.sh        # Main sync script
│   ├── heartbeat.py          # Heartbeat system
│   ├── health_server.py      # HTTP health endpoint
│   ├── monitor.py            # Monitoring & alerts
│   ├── conflict_resolver.py  # Git conflict resolution
│   ├── conflicts/            # Saved conflict versions
│   ├── backups/              # File backups
│   └── pending/              # Pending messages
├── deploy/
│   ├── setup.sh              # Setup script
│   ├── sync.service          # Systemd service
│   ├── heartbeat.service
│   ├── health-server.service
│   └── monitor.service
├── logs/
│   ├── sync.log
│   ├── heartbeat.log
│   ├── monitor.log
│   └── conflict_resolver.log
└── .sync_env                 # Environment config
```

## Maintenance

### Daily
- Check `curl http://localhost:8080/health`
- Review `logs/monitor.log` for alerts

### Weekly
- Clean old logs: `find logs -name "*.log" -mtime +7 -delete`
- Clean old conflicts: `find sync/conflicts -mtime +30 -delete`
- Review `sync/sync_state.json`

### Monthly
- Update systemd service files if needed
- Review alert frequency
- Check disk usage

## Security

- Services run as root (required for git access)
- Health endpoint binds to localhost only
- No sensitive data in logs
- Lock files prevent duplicate processes

## License

Internal use only - Helios-Chad Sync System
