#!/usr/bin/env python3
"""
Report Delivery Service for CHAD_YI
Reads reports from outbox and delivers to Telegram.
"""

import os
import time
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
OUTBOX = WORKSPACE / "agents" / "chad-yi" / "outbox"
SENT = WORKSPACE / "agents" / "chad-yi" / "sent"
LOG = WORKSPACE / "agents" / "chad-yi" / "delivery.log"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f"[{timestamp}] {msg}\n"
    with open(LOG, "a") as f:
        f.write(entry)
    print(entry.strip())

def deliver_report(filepath):
    """Deliver report to Caleb via Telegram."""
    content = filepath.read_text()
    
    # Write to Telegram message file (OpenClaw will pick this up)
    telegram_file = WORKSPACE / "TELEGRAM_MESSAGE.txt"
    telegram_file.write_text(content)
    
    log(f"Delivered: {filepath.name}")
    
    # Move to sent folder
    SENT.mkdir(parents=True, exist_ok=True)
    (SENT / filepath.name).write_text(content)
    filepath.unlink()

def main():
    log("Report delivery service started")
    
    while True:
        try:
            # Check for reports in outbox
            if OUTBOX.exists():
                reports = list(OUTBOX.glob("report-*.md"))
                
                for report in reports:
                    log(f"Found report: {report.name}")
                    deliver_report(report)
            
            # Sleep before next check
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
