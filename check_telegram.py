#!/usr/bin/env python3
"""
Quick Telegram Web check - take screenshot of CallistoFX
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("Opening Telegram Web...")
    page.goto("https://web.telegram.org")
    time.sleep(8)
    
    # Screenshot
    page.screenshot(path="/home/chad-yi/.openclaw/workspace/telegram_current.png", full_page=False)
    print("Screenshot saved: telegram_current.png")
    
    browser.close()