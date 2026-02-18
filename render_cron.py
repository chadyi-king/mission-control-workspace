#!/usr/bin/env python3
"""
Render Cron Job - Runs every minute to check system health
"""

import json
import time
import sys
from datetime import datetime

sys.path.insert(0, '/app')
from sync.redis_comm import RedisComm

def main():
    print(f"[{datetime.now().isoformat()}] Cron job running...")
    
    comm = RedisComm(node_name='helios_cron')
    
    # Check dashboard freshness
    try:
        with open('/app/data.json', 'r') as f:
            data = json.load(f)
        
        last_updated = data.get('lastUpdated', '')
        print(f"Last dashboard update: {last_updated}")
        
        # If stale, alert
        if last_updated:
            from datetime import datetime
            last = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            now = datetime.now().astimezone()
            diff_minutes = (now - last).total_seconds() / 60
            
            if diff_minutes > 10:
                print(f"ALERT: Dashboard stale for {diff_minutes:.0f} minutes")
                comm.broadcast("alert", {
                    "level": "critical",
                    "message": f"Dashboard stale for {diff_minutes:.0f} minutes",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                print("Dashboard is fresh")
    except Exception as e:
        print(f"Error checking dashboard: {e}")
    
    # Send heartbeat
    comm.broadcast("heartbeat", {
        "from": "helios_cron",
        "status": "check_complete",
        "timestamp": datetime.now().isoformat()
    })
    
    comm.stop()
    print("Cron job complete")

if __name__ == "__main__":
    main()
