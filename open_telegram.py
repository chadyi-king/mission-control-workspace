#!/usr/bin/env python3
"""
Open Telegram Web in browser and screenshot
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)  # Visible window
    page = browser.new_page()
    
    print("Opening web.telegram.org...")
    page.goto("https://web.telegram.org")
    
    # Wait for page to load
    time.sleep(5)
    
    # Take screenshot
    screenshot_path = "/home/chad-yi/.openclaw/workspace/telegram_screenshot.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"Screenshot saved: {screenshot_path}")
    
    # Keep browser open
    print("Browser open. Press Ctrl+C to close.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    browser.close()