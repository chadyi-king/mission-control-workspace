#!/usr/bin/env python3
"""
CHAD_YI Heartbeat & Reporting System
Runs every 2 hours to compile status and send reports to Caleb.
"""

import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
AGENTS_DIR = WORKSPACE / "agents"
HELIOS_OUTBOX = AGENTS_DIR / "helios" / "outbox"
DASHBOARD_DATA = WORKSPACE / "mission-control-dashboard" / "data.json"
REPORTS_DIR = AGENTS_DIR / "chad-yi" / "reports"

def now_sgt():
    """Get current time in Singapore timezone"""
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt)

def format_time(dt):
    """Format datetime for display"""
    return dt.strftime("%H:%M %Z")

def read_dashboard_data():
    """Read data.json and return stats"""
    try:
        with open(DASHBOARD_DATA) as f:
            return json.load(f)
    except:
        return {"stats": {}, "tasks": {}, "agents": {}}

def read_helios_last_audit():
    """Read most recent Helios audit report"""
    try:
        audit_files = sorted(HELIOS_OUTBOX.glob("audit-*.json"), reverse=True)
        if audit_files:
            with open(audit_files[0]) as f:
                return json.load(f)
    except:
        pass
    return {}

def count_tasks_by_status(data):
    """Count tasks by their actual status"""
    tasks = data.get("tasks", {})
    counts = {"pending": 0, "active": 0, "review": 0, "done": 0, "blocked": 0}
    
    for task_id, task in tasks.items():
        status = task.get("status", "pending")
        if status in counts:
            counts[status] += 1
    
    return counts

def get_urgent_tasks(data):
    """Get tasks with deadlines approaching"""
    tasks = data.get("tasks", {})
    urgent = []
    now = now_sgt()
    
    for task_id, task in tasks.items():
        deadline = task.get("deadline")
        if deadline:
            try:
                deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
                days_until = (deadline_dt - now.replace(tzinfo=None)).days
                
                if days_until < 0:
                    urgent.append((task_id, task, "OVERDUE", days_until))
                elif days_until <= 2:
                    urgent.append((task_id, task, f"{days_until} days", days_until))
            except:
                pass
    
    # Sort by urgency (most urgent first)
    urgent.sort(key=lambda x: x[3])
    return urgent

def get_active_agents(data):
    """Get status of core agents"""
    agents = {
        "chad-yi": {"status": "active", "task": "Monitoring & reporting"},
        "helios": {"status": "active", "task": "Running 15-min audits"},
        "cerebronn": {"status": "building", "task": "In development (VS Code)"}
    }
    
    # Check Helios last audit
    last_audit = read_helios_last_audit()
    if last_audit:
        audit_time = last_audit.get("timestamp", "unknown")
        agents["helios"]["last_audit"] = audit_time
    
    return agents

def generate_heartbeat_report():
    """Generate 2-hour heartbeat report"""
    data = read_dashboard_data()
    stats = data.get("stats", {})
    task_counts = count_tasks_by_status(data)
    urgent = get_urgent_tasks(data)
    agents = get_active_agents(data)
    now = now_sgt()
    
    report = f"""**Heartbeat — {format_time(now)}**

**Dashboard Overview**
• Total: {stats.get('total', 0)} tasks
• Pending: {task_counts['pending']} | Active: {task_counts['active']} | Review: {task_counts['review']} | Done: {task_counts['done']}

**Agent Status**
• CHAD_YI — {agents['chad-yi']['status']} | {agents['chad-yi']['task']}
• Helios — {agents['helios']['status']} | {agents['helios']['task']}
• Cerebronn — {agents['cerebronn']['status']} | {agents['cerebronn']['task']}
"""
    
    # Add urgent tasks if any
    if urgent:
        report += "\n**Urgent Deadlines**\n"
        for task_id, task, urgency, _ in urgent[:5]:  # Top 5
            title = task.get('title', 'Untitled')
            report += f"• {task_id}: {title} — **{urgency}**\n"
    
    # Add blockers if any
    blocked_tasks = [t for t in data.get("tasks", {}).values() if t.get("status") == "blocked"]
    if blocked_tasks:
        report += "\n**Blockers**\n"
        for task in blocked_tasks[:3]:
            task_id = task.get('id', 'unknown')
            title = task.get('title', 'Untitled')
            report += f"• {task_id}: {title}\n"
    
    return report

def generate_digest_report(is_morning=True):
    """Generate morning or evening digest"""
    data = read_dashboard_data()
    stats = data.get("stats", {})
    task_counts = count_tasks_by_status(data)
    urgent = get_urgent_tasks(data)
    agents = get_active_agents(data)
    now = now_sgt()
    
    period = "Morning" if is_morning else "Evening"
    
    report = f"""# {period} Digest — {now.strftime('%A, %B %d')}

## Summary
**Tasks:** {stats.get('total', 0)} total | {task_counts['pending']} pending | {task_counts['active']} active | {task_counts['review']} review | {task_counts['done']} done

## Core Agents
| Agent | Status | Current Focus |
|-------|--------|---------------|
| CHAD_YI | {agents['chad-yi']['status']} | {agents['chad-yi']['task']} |
| Helios | {agents['helios']['status']} | {agents['helios']['task']} |
| Cerebronn | {agents['cerebronn']['status']} | {agents['cerebronn']['task']} |

## Urgent Items ({len(urgent)} found)
"""
    
    if urgent:
        report += "| Task | Status | Deadline |\n|------|--------|----------|\n"
        for task_id, task, urgency, _ in urgent[:10]:
            title = task.get('title', 'Untitled')[:40]
            status = task.get('status', 'unknown')
            report += f"| {task_id} | {title} | {urgency} |\n"
    else:
        report += "_No urgent deadlines._\n"
    
    # Recent activity
    report += "\n## Recent Activity\n"
    report += "_Check Helios audit reports for detailed activity._\n"
    
    # Next actions
    if is_morning:
        report += "\n## Today's Focus\n"
        report += "• Review urgent tasks\n"
        report += "• Monitor Cerebronn build progress\n"
        report += "• Check for blockers\n"
    else:
        report += "\n## Tomorrow's Priorities\n"
        report += "• Review completed tasks\n"
        report += "• Plan next agent build (Quanta)\n"
        report += "• Archive completed work\n"
    
    return report

def send_report(report, report_type="heartbeat"):
    """Send report to Caleb via file-based messaging"""
    timestamp = now_sgt().strftime("%Y%m%d-%H%M%S")
    
    # Write to my outbox (for tracking)
    outbox_file = AGENTS_DIR / "chad-yi" / "outbox" / f"{report_type}-{timestamp}.md"
    outbox_file.parent.mkdir(parents=True, exist_ok=True)
    outbox_file.write_text(report)
    
    # For now, print to stdout (will be sent via message tool in production)
    print(f"\n{'='*60}")
    print(f"CHAD_YI {report_type.upper()} REPORT")
    print(f"{'='*60}")
    print(report)
    print(f"{'='*60}\n")
    
    return outbox_file

def main():
    """Main entry point for cron job"""
    now = now_sgt()
    hour = now.hour
    
    # Determine report type based on time
    if hour == 8:  # 8 AM SGT - Morning Digest
        report = generate_digest_report(is_morning=True)
        send_report(report, "morning-digest")
    elif hour == 21:  # 9 PM SGT - Evening Digest
        report = generate_digest_report(is_morning=False)
        send_report(report, "evening-digest")
    else:
        # Regular 2-hour heartbeat
        report = generate_heartbeat_report()
        send_report(report, "heartbeat")

if __name__ == "__main__":
    main()
