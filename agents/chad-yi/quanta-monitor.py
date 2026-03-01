#!/usr/bin/env python3
"""
CHAD_YI Quanta Trade Monitor
Polls inbox every 5 minutes for Quanta trade alerts and sends to Caleb.

Trade file patterns:
- quanta-trade-opened-*.md → New trade placed
- quanta-tp1-*.md → TP1 hit, breakeven set
- quanta-tp2/3/4-*.md → Further profits
- quanta-runner-*.md → Runner milestone
- quanta-trade-closed-*.md → Trade summary
"""

import json
import os
import time
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
    """Load list of already processed files"""
    if PROCESSED_FILE.exists():
        return set(PROCESSED_FILE.read_text().strip().split("\n"))
    return set()

def mark_processed(filename):
    """Mark file as processed"""
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{filename}\n")

def archive_file(filepath):
    """Move file to archive"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_name = f"{timestamp}-{filepath.name}"
    filepath.rename(ARCHIVE_DIR / new_name)

def parse_trade_alert(filepath):
    """Parse a Quanta trade alert file"""
    content = filepath.read_text()
    lines = content.strip().split("\n")
    
    # Extract alert type from filename
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
    
    # Extract symbol and direction from content
    symbol = "Unknown"
    direction = ""
    for line in lines:
        if "Symbol" in line and "|" in line:
            symbol = line.split("|")[2].strip().strip("`")
        if "Direction" in line and "|" in line:
            direction = line.split("|")[2].strip().strip("`")
    
    return {
        "type": alert_type,
        "symbol": symbol,
        "direction": direction,
        "content": content,
        "filename": filename
    }

def generate_telegram_message(alert):
    """Generate Telegram message from alert"""
    msg = f"""**{alert['type']}**

**{alert['symbol']}** {alert['direction']}

_Time: {format_time(now_sgt())}_

{alert['content'][:500]}"""
    return msg

def check_quanta_alerts():
    """Check for new Quanta alerts"""
    processed = get_processed_files()
    new_alerts = []
    
    # Find all Quanta files
    for filepath in sorted(QUANTA_INBOX.glob("quanta-*.md")):
        if filepath.name in processed:
            continue
        
        alert = parse_trade_alert(filepath)
        new_alerts.append((filepath, alert))
        mark_processed(filepath.name)
    
    return new_alerts

def main():
    """Main polling loop - runs continuously"""
    print(f"[{format_time(now_sgt())}] Quanta Monitor starting...")
    
    while True:
        try:
            alerts = check_quanta_alerts()
            
            if alerts:
                print(f"[{format_time(now_sgt())}] Found {len(alerts)} new Quanta alert(s)")
                
                for filepath, alert in alerts:
                    # Generate message for Caleb
                    msg = generate_telegram_message(alert)
                    
                    # Print (will be sent via Telegram)
                    print(f"\n{'='*60}")
                    print(f"QUANTA ALERT - {format_time(now_sgt())}")
                    print(f"{'='*60}")
                    print(msg)
                    print(f"{'='*60}\n")
                    
                    # Archive the file
                    archive_file(filepath)
                    print(f"  Archived: {filepath.name}")
            else:
                # No new alerts - just log occasionally
                if datetime.now().second % 60 == 0:  # Once per minute
                    print(f"[{format_time(now_sgt())}] No new alerts")
            
            # Sleep 5 minutes
            time.sleep(300)
            
        except Exception as e:
            print(f"[{format_time(now_sgt())}] Error: {e}")
            time.sleep(60)  # Retry in 1 min on error

if __name__ == "__main__":
    main()
