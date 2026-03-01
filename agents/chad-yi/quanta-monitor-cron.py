#!/usr/bin/env python3
"""
CHAD_YI Quanta Trade Monitor (Cron version)
Called every 5 minutes via cron. Checks for new Quanta alerts.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
QUANTA_INBOX = WORKSPACE / "agents" / "chad-yi" / "inbox"
ARCHIVE_DIR = WORKSPACE / "agents" / "chad-yi" / "archive" / "quanta"
PROCESSED_FILE = WORKSPACE / "agents" / "chad-yi" / ".quanta_processed"

def now_sgt():
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt)

def format_time(dt):
    return dt.strftime("%H:%M")

def get_processed_files():
    if PROCESSED_FILE.exists():
        return set(PROCESSED_FILE.read_text().strip().split("\n"))
    return set()

def mark_processed(filename):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{filename}\n")

def archive_file(filepath):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_name = f"{timestamp}-{filepath.name}"
    filepath.rename(ARCHIVE_DIR / new_name)

def parse_trade_alert(filepath):
    content = filepath.read_text()
    filename = filepath.name
    
    if "trade-opened" in filename:
        alert_type = "🟢 TRADE OPENED"
    elif "tp1" in filename:
        alert_type = "💰 TP1 HIT (Risk-Free)"
    elif "tp2" in filename:
        alert_type = "💰💰 TP2 HIT"
    elif "tp3" in filename:
        alert_type = "💰💰💰 TP3 HIT"
    elif "tp4" in filename:
        alert_type = "💰💰💰💰 TP4 HIT"
    elif "runner" in filename:
        alert_type = "🏃 RUNNER UPDATE"
    elif "trade-closed" in filename:
        alert_type = "🔴 TRADE CLOSED"
    else:
        alert_type = "📊 QUANTA ALERT"
    
    symbol = "Unknown"
    direction = ""
    for line in content.split("\n"):
        if "Symbol" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                symbol = parts[2].strip().strip("`")
        if "Direction" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                direction = parts[2].strip().strip("`")
    
    return {
        "type": alert_type,
        "symbol": symbol,
        "direction": direction,
        "content": content,
        "filename": filename
    }

def send_telegram_message(alert):
    """Print message that will be sent to Caleb via Telegram"""
    msg = f"""**QUANTA ALERT — {format_time(now_sgt())}**

**{alert['type']}**
**{alert['symbol']}** {alert['direction']}

{alert['content'][:400]}

---
_From QUANTA v3_"""
    
    print(f"\n{'='*60}")
    print(msg)
    print(f"{'='*60}\n")

def main():
    processed = get_processed_files()
    new_alerts = []
    
    # Find all Quanta files
    for filepath in sorted(QUANTA_INBOX.glob("quanta-*.md")):
        if filepath.name in processed:
            continue
        
        alert = parse_trade_alert(filepath)
        new_alerts.append((filepath, alert))
        mark_processed(filepath.name)
    
    if new_alerts:
        print(f"[{format_time(now_sgt())}] Found {len(new_alerts)} new Quanta alert(s)")
        
        for filepath, alert in new_alerts:
            # Generate and print message (will route to Telegram)
            send_telegram_message(alert)
            
            # Archive the file
            archive_file(filepath)
            print(f"  Archived: {filepath.name}")
    else:
        # Only log occasionally to reduce noise
        minute = now_sgt().minute
        if minute % 30 == 0:  # Log every 30 minutes (6th check)
            print(f"[{format_time(now_sgt())}] No new Quanta alerts")

if __name__ == "__main__":
    main()
