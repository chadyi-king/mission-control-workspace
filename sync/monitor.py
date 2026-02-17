#!/usr/bin/env python3
"""
Monitor for Helios-Chad Sync System
Monitors both sides, alerts on issues
"""

import json
import time
import os
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading

# Configuration
LOG_DIR = Path("/home/chad-yi/.openclaw/workspace/logs")
STATE_DIR = Path("/home/chad-yi/.openclaw/workspace/sync")
ALERT_COOLDOWN = 300  # 5 minutes between alerts
HEARTBEAT_TIMEOUT = 180  # 3 minutes
MAX_SYNC_FAILURES = 3

# Caleb's Telegram ID
CALEB_TELEGRAM_ID = os.environ.get("CALEB_TELEGRAM_ID", "512366713")

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("monitor")


class AlertManager:
    def __init__(self):
        self.last_alerts = {}
        self.alert_cooldown = ALERT_COOLDOWN
    
    def can_alert(self, alert_type):
        """Check if we can send an alert (respect cooldown)"""
        now = time.time()
        last_alert = self.last_alerts.get(alert_type, 0)
        
        if now - last_alert >= self.alert_cooldown:
            self.last_alerts[alert_type] = now
            return True
        return False
    
    def send_alert(self, message, alert_type="general"):
        """Send alert to Caleb via Telegram"""
        if not self.can_alert(alert_type):
            logger.info(f"Alert suppressed (cooldown): {message}")
            return False
        
        try:
            # Use openclaw message command
            cmd = [
                "openclaw", "message", "send",
                "--channel", "telegram",
                "--target", CALEB_TELEGRAM_ID,
                "--message", f"🚨 SYNC ALERT: {message}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Alert sent: {message}")
                return True
            else:
                logger.error(f"Failed to send alert: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def send_recovery_notice(self, message):
        """Send recovery notice"""
        try:
            cmd = [
                "openclaw", "message", "send",
                "--channel", "telegram",
                "--target", CALEB_TELEGRAM_ID,
                "--message", f"✅ SYNC RECOVERY: {message}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to send recovery notice: {e}")
            return False


class SyncMonitor:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.running = False
        self.node_name = os.environ.get("NODE_NAME", "unknown")
        self.failure_counts = {
            "sync": 0,
            "heartbeat": 0,
            "git": 0
        }
        self.alert_states = {
            "sync": False,
            "heartbeat": False,
            "git": False
        }
    
    def check_heartbeat(self):
        """Check if heartbeats are being received"""
        try:
            # Check peer heartbeat files
            for peer_file in STATE_DIR.glob("peer_*_state.json"):
                with open(peer_file) as f:
                    data = json.load(f)
                    received_at = datetime.fromisoformat(
                        data["received_at"].replace('Z', '+00:00')
                    )
                    
                    elapsed = (datetime.utcnow() - received_at).total_seconds()
                    peer_name = peer_file.stem.replace("peer_", "").replace("_state", "")
                    
                    if elapsed > HEARTBEAT_TIMEOUT:
                        self.failure_counts["heartbeat"] += 1
                        if self.failure_counts["heartbeat"] >= 2 and not self.alert_states["heartbeat"]:
                            self.alert_manager.send_alert(
                                f"No heartbeat from {peer_name} for {int(elapsed/60)} minutes",
                                "heartbeat"
                            )
                            self.alert_states["heartbeat"] = True
                        return False
                    else:
                        # Reset on success
                        if self.alert_states["heartbeat"]:
                            self.alert_manager.send_recovery_notice(
                                f"Heartbeat from {peer_name} restored"
                            )
                            self.alert_states["heartbeat"] = False
                        self.failure_counts["heartbeat"] = 0
                        return True
                        
        except Exception as e:
            logger.error(f"Failed to check heartbeat: {e}")
            return False
        
        return True
    
    def check_sync_status(self):
        """Check if sync is working properly"""
        try:
            sync_state = STATE_DIR / "sync_state.json"
            if not sync_state.exists():
                return True  # No sync yet, not an error
            
            with open(sync_state) as f:
                data = json.load(f)
                last_sync = datetime.fromisoformat(
                    data["last_sync"].replace('Z', '+00:00')
                )
                
                elapsed = (datetime.utcnow() - last_sync).total_seconds()
                
                if elapsed > 600:  # 10 minutes
                    self.failure_counts["sync"] += 1
                    if self.failure_counts["sync"] >= MAX_SYNC_FAILURES and not self.alert_states["sync"]:
                        self.alert_manager.send_alert(
                            f"Sync has not completed in {int(elapsed/60)} minutes",
                            "sync"
                        )
                        self.alert_states["sync"] = True
                    return False
                else:
                    if self.alert_states["sync"]:
                        self.alert_manager.send_recovery_notice("Sync restored")
                        self.alert_states["sync"] = False
                    self.failure_counts["sync"] = 0
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to check sync status: {e}")
            return False
        
        return True
    
    def check_git_conflicts(self):
        """Check for unresolved git conflicts"""
        try:
            result = subprocess.run(
                ["git", "-C", str(STATE_DIR.parent), "diff", "--name-only", "--diff-filter=U"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                conflicts = result.stdout.strip().split('\n')
                self.failure_counts["git"] += 1
                
                if self.failure_counts["git"] >= 2 and not self.alert_states["git"]:
                    self.alert_manager.send_alert(
                        f"Unresolved git conflicts: {', '.join(conflicts[:3])}",
                        "git"
                    )
                    self.alert_states["git"] = True
                return False
            else:
                if self.alert_states["git"]:
                    self.alert_manager.send_recovery_notice("Git conflicts resolved")
                    self.alert_states["git"] = False
                self.failure_counts["git"] = 0
                return True
                
        except Exception as e:
            logger.error(f"Failed to check git conflicts: {e}")
            return False
    
    def check_process_health(self):
        """Check if sync processes are running"""
        processes_to_check = ["robust_sync.sh", "heartbeat.py", "health_server.py"]
        missing = []
        
        for proc in processes_to_check:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", proc],
                    capture_output=True, timeout=5
                )
                if result.returncode != 0:
                    missing.append(proc)
            except Exception as e:
                logger.error(f"Failed to check process {proc}: {e}")
        
        if missing:
            self.alert_manager.send_alert(
                f"Missing processes: {', '.join(missing)}",
                "process"
            )
            return False
        
        return True
    
    def run_checks(self):
        """Run all health checks"""
        results = {
            "heartbeat": self.check_heartbeat(),
            "sync": self.check_sync_status(),
            "git": self.check_git_conflicts(),
            "process": self.check_process_health(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Save status
        status_file = STATE_DIR / "monitor_status.json"
        with open(status_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Monitor started")
        
        while self.running:
            try:
                results = self.run_checks()
                
                # Log summary
                failed = [k for k, v in results.items() if v is False]
                if failed:
                    logger.warning(f"Check failures: {', '.join(failed)}")
                else:
                    logger.debug("All checks passed")
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            # Check every 30 seconds
            time.sleep(30)
    
    def start(self):
        """Start the monitor"""
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the monitor"""
        self.running = False
        logger.info("Monitor stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Monitor")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon")
    parser.add_argument("--check", action="store_true",
                       help="Run checks once and exit")
    
    args = parser.parse_args()
    
    monitor = SyncMonitor()
    
    if args.check:
        results = monitor.run_checks()
        print(json.dumps(results, indent=2))
        return 0 if all(v for k, v in results.items() if k != "timestamp") else 1
    
    elif args.daemon:
        monitor.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            monitor.stop()
    
    else:
        # Default: run checks once
        results = monitor.run_checks()
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    exit(main())
