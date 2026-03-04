#!/usr/bin/env python3
"""
CHAD_YI Heartbeat - PROPERLY FIXED
Sends reports to Caleb's Telegram at scheduled times.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
INBOX = WORKSPACE / "agents" / "chad-yi" / "inbox"
OUTBOX = WORKSPACE / "agents" / "chad-yi" / "outbox"

def sgt_now():
    return datetime.now(timezone(timedelta(hours=8)))

def get_agent_status():
    """Check agent statuses."""
    agents = {}
    for agent in ["cerebronn", "helios", "forger", "quanta-v3"]:
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", agent],
                capture_output=True,
                text=True,
                timeout=5
            )
            agents[agent] = result.stdout.strip()
        except:
            agents[agent] = "unknown"
    return agents

def get_task_stats():
    """Get task stats from dashboard data."""
    try:
        data_file = WORKSPACE / "mission-control-dashboard" / "data.json"
        if data_file.exists():
            data = json.loads(data_file.read_text())
            tasks = data.get("tasks", {})
            stats = {"total": len(tasks), "pending": 0, "active": 0, "blocked": 0}
            for t in tasks.values():
                status = t.get("status", "").lower()
                if status == "pending":
                    stats["pending"] += 1
                elif status == "active":
                    stats["active"] += 1
                elif status in ["blocked", "waiting"]:
                    stats["blocked"] += 1
            return stats
    except Exception as e:
        print(f"Error reading tasks: {e}", file=sys.stderr)
    return {"total": "?", "pending": "?", "active": "?", "blocked": "?"}

def generate_report(report_type):
    """Generate status report."""
    now = sgt_now()
    time_str = now.strftime("%H:%M")
    
    agents = get_agent_status()
    stats = get_task_stats()
    
    # Format based on type
    if report_type == "morning":
        header = f"🌅 MORNING DIGEST — {time_str} SGT"
    elif report_type == "evening":
        header = f"🌙 EVENING DIGEST — {time_str} SGT"
    else:
        header = f"📊 HEARTBEAT — {time_str} SGT"
    
    report = f"""# {header}

## Task Overview
• **Total:** {stats['total']} | **Pending:** {stats['pending']} | **Active:** {stats['active']} | **Blocked:** {stats['blocked']}

## Agent Status
| Agent | Status |
|-------|--------|
| Cerebronn | {agents.get('cerebronn', '?')} |
| Helios | {agents.get('helios', '?')} |
| Forger | {agents.get('forger', '?')} |
| Quanta | {agents.get('quanta-v3', '?')} |

## Dashboard
https://mission-control-dashboard-hf0r.onrender.com/

---
*Sent at {time_str}*
"""
    return report

def main():
    report_type = sys.argv[2] if len(sys.argv) > 2 else "heartbeat"
    
    # Generate report
    report = generate_report(report_type)
    
    # Write to outbox for Telegram delivery
    timestamp = sgt_now().strftime("%Y%m%d-%H%M")
    report_file = OUTBOX / f"report-{report_type}-{timestamp}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report)
    
    # Also log it
    log_file = WORKSPACE / "agents" / "chad-yi" / "heartbeat.log"
    with open(log_file, "a") as f:
        f.write(f"[{sgt_now().strftime('%H:%M')}] {report_type} report generated\n")
    
    print(f"Report generated: {report_file}")

if __name__ == "__main__":
    main()
