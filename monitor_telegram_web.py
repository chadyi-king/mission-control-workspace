#!/usr/bin/env python3
"""
Open Telegram Web and monitor for messages
"""

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

LOG_FILE = "/home/chad-yi/.openclaw/workspace/agents/quanta/logs/telegram_web_messages.jsonl"

def log_message(text):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": text
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged message")

with sync_playwright() as p:
    # Launch headless browser (no GUI needed)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("Opening web.telegram.org...")
    page.goto("https://web.telegram.org")
    
    # Wait for QR code or login screen
    print("Waiting for login screen...")
    time.sleep(10)
    
    # Take screenshot to see current state
    screenshot_path = "/home/chad-yi/.openclaw/workspace/telegram_login_screenshot.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"Screenshot saved: {screenshot_path}")
    print("Check the screenshot - if you see QR code, scan it with your phone")
    
    # Keep browser open for monitoring
    print("\nBrowser is open. Press Ctrl+C to stop.")
    print("Once you're logged in, I can start monitoring the channel.")
    
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    
    browser.close()