#!/usr/bin/env python3
"""
CHAD_YI Heartbeat & Reporting System
Task-focused reports for Caleb.

Schedule:
- 08:00 - Morning Digest
- 10:00, 12:00, 14:00, 16:00, 18:00, 20:00 - Heartbeats (every 2h)
- 22:00 - Evening Digest
- 03:00 - Overnight Heartbeat (5h after evening)

Usage: python chad-yi-heartbeat.py --type [morning|evening|heartbeat]
"""

import json
import os
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
AGENTS_DIR = WORKSPACE / "agents"
HELIOS_OUTBOX = AGENTS_DIR / "helios" / "outbox"
DASHBOARD_DATA = WORKSPACE / "mission-control-dashboard" / "data.json"

# Telegram credentials (same bot Helios uses to reach Caleb)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8693482792:AAGNa21qo-fNGuPSDE5j5-828QAn7JSubdU")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID",   "8583017204")
TELEGRAM_MAX_CHARS = 4000  # Telegram limit is 4096; keep headroom

def now_sgt():
    """Get current time in Singapore timezone"""
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt)

def format_time(dt):
    """Format datetime for display"""
    return dt.strftime("%H:%M")

def read_dashboard_data():
    """Read data.json and return stats"""
    try:
        with open(DASHBOARD_DATA) as f:
            return json.load(f)
    except:
        return {"stats": {}, "tasks": {}, "agents": {}, "workflow": {}}

def get_tasks_by_status(data):
    """Get tasks organized by status"""
    tasks = data.get("tasks", {})
    workflow = data.get("workflow", {})
    
    # Get tasks from workflow arrays
    pending = [tasks.get(tid) for tid in workflow.get("pending", []) if tid in tasks]
    active = [tasks.get(tid) for tid in workflow.get("active", []) if tid in tasks]
    review = [tasks.get(tid) for tid in workflow.get("review", []) if tid in tasks]
    done = [tasks.get(tid) for tid in workflow.get("done", []) if tid in tasks]
    
    # Also check for blocked tasks
    blocked = [t for t in tasks.values() if t.get("status") == "blocked"]
    
    return {
        "pending": pending,
        "active": active,
        "review": review,
        "done": done,
        "blocked": blocked
    }

def get_urgent_tasks(tasks_by_status):
    """Get tasks that need immediate attention"""
    urgent = []
    now = now_sgt().replace(tzinfo=None)
    
    # Check all non-done tasks
    for status in ["pending", "active", "review", "blocked"]:
        for task in tasks_by_status.get(status, []):
            deadline = task.get("deadline")
            if deadline:
                try:
                    deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
                    days_until = (deadline_dt - now).days
                    
                    if days_until < 0:
                        urgent.append((task, "🔴 OVERDUE", days_until))
                    elif days_until <= 2:
                        urgent.append((task, f"🟡 {days_until}d", days_until))
                except:
                    pass
    
    # Sort by urgency
    urgent.sort(key=lambda x: x[2])
    return urgent

def get_tasks_needing_input(tasks_by_status):
    """Get tasks that need Caleb's input/decision"""
    needing_input = []
    
    # Pending tasks need assignment/decision
    for task in tasks_by_status.get("pending", []):
        if task.get("needs_input") or task.get("assignee") == "Caleb":
            needing_input.append(task)
    
    # Blocked tasks need unblock
    for task in tasks_by_status.get("blocked", []):
        needing_input.append(task)
    
    return needing_input

def format_task_line(task, include_deadline=True):
    """Format a single task for display"""
    task_id = task.get("id", "unknown")
    title = task.get("title", "Untitled")
    assignee = task.get("assignee", "Unassigned")
    deadline = task.get("deadline", "")
    status = task.get("status", "pending")
    
    # Truncate title if too long
    title_display = title[:50] + "..." if len(title) > 50 else title
    
    line = f"**{task_id}** — {title_display}"
    
    if assignee and assignee != "Unassigned":
        line += f" *(→ {assignee})*"
    
    if include_deadline and deadline:
        line += f" `[{deadline}]`"
    
    return line

def generate_task_focused_report(report_type="heartbeat"):
    """Generate task-focused report with icons"""
    data = read_dashboard_data()
    tasks_by_status = get_tasks_by_status(data)
    urgent = get_urgent_tasks(tasks_by_status)
    needing_input = get_tasks_needing_input(tasks_by_status)
    now = now_sgt()
    
    is_morning = report_type == "morning"
    is_evening = report_type == "evening"
    
    # Header
    if is_morning:
        header = f"🌅 **Morning Digest** — {now.strftime('%A, %B %d')}"
    elif is_evening:
        header = f"🌙 **Evening Digest** — {now.strftime('%A, %B %d')}"
    else:
        header = f"💓 **Heartbeat** — {format_time(now)}"
    
    report = f"{header}\n\n"
    
    # ─────────────────────────────────────────
    # URGENT DEADLINES
    # ─────────────────────────────────────────
    if urgent:
        report += "## ⚠️ Urgent Deadlines\n\n"
        for task, urgency, _ in urgent[:8]:  # Top 8
            task_line = format_task_line(task)
            report += f"{urgency} {task_line}\n"
        report += "\n"
    
    # ─────────────────────────────────────────
    # NEEDS YOUR INPUT
    # ─────────────────────────────────────────
    if needing_input:
        report += "## 👤 Needs Your Input\n\n"
        for task in needing_input[:5]:
            task_line = format_task_line(task)
            reason = ""
            if task.get("status") == "blocked":
                reason = " *(blocked)*"
            report += f"☐ {task_line}{reason}\n"
        report += "\n"
    
    # ─────────────────────────────────────────
    # IN REVIEW (Needs Your Review)
    # ─────────────────────────────────────────
    if tasks_by_status["review"]:
        report += "## 👀 In Review (Check & Approve)\n\n"
        for task in tasks_by_status["review"][:5]:
            task_line = format_task_line(task, include_deadline=False)
            report += f"☐ {task_line}\n"
        report += "\n"
    
    # ─────────────────────────────────────────
    # ACTIVE TODAY
    # ─────────────────────────────────────────
    if tasks_by_status["active"]:
        report += "## ▶️ Active Today\n\n"
        for task in tasks_by_status["active"][:5]:
            task_line = format_task_line(task, include_deadline=False)
            report += f"▶ {task_line}\n"
        report += "\n"
    
    # ─────────────────────────────────────────
    # QUICK STATS
    # ─────────────────────────────────────────
    total = len(data.get("tasks", {}))
    report += "## 📊 Quick Stats\n\n"
    report += f"```\n"
    report += f"Total:    {total:3d} tasks\n"
    report += f"Pending:  {len(tasks_by_status['pending']):3d}\n"
    report += f"Active:   {len(tasks_by_status['active']):3d}\n"
    report += f"Review:   {len(tasks_by_status['review']):3d}\n"
    report += f"Blocked:  {len(tasks_by_status['blocked']):3d}\n"
    report += f"Done:     {len(tasks_by_status['done']):3d}\n"
    report += f"```\n\n"
    
    # ─────────────────────────────────────────
    # AGENT STATUS (Secondary)
    # ─────────────────────────────────────────
    report += "## 🤖 Agent Status\n\n"
    report += "• ✅ **CHAD_YI** — Active | Task-focused reporting\n"
    report += "• ✅ **Helios** — Auditing every 15 min\n"
    report += "• 🔧 **Cerebronn** — Building in VS Code\n"
    report += "\n"
    
    # ─────────────────────────────────────────
    # TODAY'S FOCUS (Morning only)
    # ─────────────────────────────────────────
    if is_morning:
        report += "## 🎯 Today's Focus\n\n"
        if urgent:
            report += "1. Address urgent/overdue deadlines\n"
        if needing_input:
            report += "2. Review tasks needing your input\n"
        if tasks_by_status["review"]:
            report += "3. Approve items in review\n"
        report += "4. Monitor Cerebronn build progress\n"
        report += "\n"
    
    # ─────────────────────────────────────────
    # TOMORROW PREVIEW (Evening only)
    # ─────────────────────────────────────────
    if is_evening:
        report += "## 📅 Tomorrow\n\n"
        report += "_Review today's progress. Plan tomorrow's priorities._\n\n"
    
    return report

def send_telegram(text: str) -> bool:
    """Send a message to Caleb via the Mission Control Telegram bot."""
    if not HAS_REQUESTS or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[telegram] requests not available or credentials missing — skipping")
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if r.ok:
            print(f"  [telegram] Sent to Caleb — {r.status_code}")
            return True
        else:
            print(f"  [telegram] Send failed: {r.status_code} {r.text[:120]}")
            return False
    except Exception as e:
        print(f"  [telegram] Error: {e}")
        return False


def drop_cerebronn_session_note(report: str, report_type: str, timestamp: str):
    """Write a compact session note to Cerebronn's inbox so the brain learns what Chad reported."""
    cerebronn_inbox = AGENTS_DIR / "cerebronn" / "inbox"
    cerebronn_inbox.mkdir(parents=True, exist_ok=True)
    note_path = cerebronn_inbox / f"chad-session-{report_type}-{timestamp}.md"
    # Keep it short — just first 1200 chars of report to avoid inbox bloat
    snippet = report[:1200] + ("\n…(truncated)" if len(report) > 1200 else "")
    note = f"# Chad-Yi Session Note — {report_type} {timestamp}\n\nChad sent this {report_type} report to Caleb at {timestamp} SGT.\n\n---\n\n{snippet}\n"
    try:
        note_path.write_text(note)
        print(f"  [cerebronn] Session note dropped: {note_path.name}")
    except Exception as e:
        print(f"  [cerebronn] Could not drop session note: {e}")


def send_report(report, report_type="heartbeat"):
    """Send report to Caleb via Telegram and write to outbox for tracking."""
    timestamp = now_sgt().strftime("%Y%m%d-%H%M")

    # Write to outbox for tracking
    outbox_file = AGENTS_DIR / "chad-yi" / "outbox" / f"{report_type}-{timestamp}.md"
    outbox_file.parent.mkdir(parents=True, exist_ok=True)
    outbox_file.write_text(report)

    # Drop a compact note in Cerebronn's inbox — keeps the brain informed
    drop_cerebronn_session_note(report, report_type, timestamp)

    # Trim to Telegram char limit if needed
    tg_text = report if len(report) <= TELEGRAM_MAX_CHARS else report[:TELEGRAM_MAX_CHARS] + "\n…_(truncated)_"

    # Send to Caleb via Telegram
    ok = send_telegram(tg_text)

    # Always print to stdout (captured in cron log)
    print(f"\n{'='*60}")
    print(f"CHAD_YI {report_type.upper()} REPORT — telegram={'sent' if ok else 'FAILED'}")
    print(f"{'='*60}")
    print(report)
    print(f"{'='*60}\n")

    return outbox_file

def main():
    parser = argparse.ArgumentParser(description="CHAD_YI Heartbeat System")
    parser.add_argument("--type", choices=["morning", "evening", "heartbeat"], 
                       default="heartbeat", help="Type of report to generate")
    args = parser.parse_args()
    
    report = generate_task_focused_report(args.type)
    send_report(report, args.type)

if __name__ == "__main__":
    main()
