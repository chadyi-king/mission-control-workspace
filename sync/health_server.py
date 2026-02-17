#!/usr/bin/env python3
"""
Health Check HTTP Server
Provides /health endpoint for monitoring sync status
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import logging

# Configuration
HEALTH_PORT = 8080
STATE_DIR = Path("/root/.openclaw/workspace/sync")
LOG_DIR = Path("/root/.openclaw/workspace/logs")

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "health_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_server")

class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/status':
            self.send_detailed_status()
        elif self.path == '/metrics':
            self.send_metrics()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Return basic health status"""
        status = self.get_health_status()
        
        self.send_response(200 if status["status"] == "ok" else 503)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        response = json.dumps(status, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_detailed_status(self):
        """Return detailed status information"""
        status = self.get_detailed_status()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        response = json.dumps(status, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_metrics(self):
        """Return Prometheus-compatible metrics"""
        metrics = self.get_prometheus_metrics()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        
        self.wfile.write(metrics.encode('utf-8'))
    
    def get_health_status(self):
        """Get current health status"""
        node_name = os.environ.get('NODE_NAME', 'unknown')
        
        # Check last sync time
        last_sync = self.get_last_sync_time()
        messages_pending = self.get_pending_messages_count()
        
        # Determine status
        status = "ok"
        if last_sync:
            elapsed = (datetime.utcnow() - last_sync).total_seconds()
            if elapsed > 300:  # 5 minutes
                status = "error"
            elif elapsed > 120:  # 2 minutes
                status = "degraded"
        
        # Get uptime if available
        uptime = self.get_uptime()
        
        return {
            "status": status,
            "node": node_name,
            "last_sync": last_sync.isoformat() + "Z" if last_sync else None,
            "messages_pending": messages_pending,
            "uptime": uptime,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_detailed_status(self):
        """Get detailed status information"""
        basic = self.get_health_status()
        
        # Add heartbeat info
        heartbeat_status = self.get_heartbeat_status()
        
        # Add sync info
        sync_info = self.get_sync_info()
        
        # Add git status
        git_status = self.get_git_status()
        
        return {
            **basic,
            "heartbeat": heartbeat_status,
            "sync": sync_info,
            "git": git_status
        }
    
    def get_prometheus_metrics(self):
        """Generate Prometheus metrics"""
        node = os.environ.get('NODE_NAME', 'unknown')
        status = self.get_health_status()
        
        metrics = []
        
        # Health status metric
        health_value = 1 if status["status"] == "ok" else 0
        metrics.append(f'sync_health{{node="{node}"}} {health_value}')
        
        # Pending messages
        metrics.append(f'sync_pending_messages{{node="{node}"}} {status["messages_pending"]}')
        
        # Uptime
        if status["uptime"]:
            metrics.append(f'sync_uptime_seconds{{node="{node}"}} {status["uptime"]}')
        
        # Last sync timestamp
        if status["last_sync"]:
            last_sync_ts = datetime.fromisoformat(status["last_sync"].replace('Z', '+00:00'))
            metrics.append(f'sync_last_sync_timestamp{{node="{node}"}} {last_sync_ts.timestamp()}')
        
        return '\n'.join(metrics)
    
    def get_last_sync_time(self):
        """Get last sync time from state file"""
        try:
            sync_state = STATE_DIR / "sync_state.json"
            if sync_state.exists():
                with open(sync_state) as f:
                    data = json.load(f)
                    last_sync = data.get("last_sync")
                    if last_sync:
                        return datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Failed to read sync state: {e}")
        return None
    
    def get_pending_messages_count(self):
        """Get count of pending messages"""
        try:
            pending_dir = STATE_DIR / "pending"
            if pending_dir.exists():
                return len(list(pending_dir.glob("*.json")))
        except Exception as e:
            logger.error(f"Failed to count pending messages: {e}")
        return 0
    
    def get_uptime(self):
        """Get process uptime"""
        try:
            with open('/proc/uptime') as f:
                return float(f.read().split()[0])
        except:
            return None
    
    def get_heartbeat_status(self):
        """Get heartbeat status from state files"""
        status = {}
        
        try:
            # Check local heartbeat
            hb_file = STATE_DIR / "heartbeat_state.json"
            if hb_file.exists():
                with open(hb_file) as f:
                    status["local"] = json.load(f)
            
            # Check peer heartbeats
            for peer_file in STATE_DIR.glob("peer_*_state.json"):
                peer_name = peer_file.stem.replace("peer_", "").replace("_state", "")
                with open(peer_file) as f:
                    status[f"peer_{peer_name}"] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to get heartbeat status: {e}")
        
        return status
    
    def get_sync_info(self):
        """Get sync information"""
        info = {
            "sync_in_progress": False,
            "last_error": None,
            "sync_count_today": 0
        }
        
        try:
            sync_log = LOG_DIR / "sync.log"
            if sync_log.exists():
                # Count syncs today
                today = datetime.utcnow().strftime("%Y-%m-%d")
                with open(sync_log) as f:
                    content = f.read()
                    info["sync_count_today"] = content.count(f"{today} - INFO - Sync completed")
            
            # Check for sync.lock
            lock_file = STATE_DIR / "sync.lock"
            info["sync_in_progress"] = lock_file.exists()
            
        except Exception as e:
            logger.error(f"Failed to get sync info: {e}")
        
        return info
    
    def get_git_status(self):
        """Get git repository status"""
        import subprocess
        
        status = {
            "branch": None,
            "dirty": False,
            "ahead": 0,
            "behind": 0
        }
        
        try:
            repo_path = Path("/root/.openclaw/workspace")
            
            # Get current branch
            result = subprocess.run(
                ["git", "-C", str(repo_path), "branch", "--show-current"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                status["branch"] = result.stdout.strip()
            
            # Check if dirty
            result = subprocess.run(
                ["git", "-C", str(repo_path), "status", "--porcelain"],
                capture_output=True, text=True, timeout=5
            )
            status["dirty"] = len(result.stdout.strip()) > 0
            
        except Exception as e:
            logger.error(f"Failed to get git status: {e}")
        
        return status


class HealthServer:
    def __init__(self, port=HEALTH_PORT):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the health server"""
        self.server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"Health server started on port {self.port}")
    
    def stop(self):
        """Stop the health server"""
        if self.server:
            self.server.shutdown()
            logger.info("Health server stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Check Server")
    parser.add_argument("--port", type=int, default=HEALTH_PORT,
                       help=f"Port to listen on (default: {HEALTH_PORT})")
    
    args = parser.parse_args()
    
    server = HealthServer(args.port)
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
