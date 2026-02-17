#!/usr/bin/env python3
"""
Login to Telegram Web with phone number
"""

from playwright.sync_api import sync_playwright
import time

PHONE = "+6591593838"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("Opening Telegram Web...")
    page.goto("https://web.telegram.org")
    time.sleep(5)
    
    # Click "LOG IN BY PHONE NUMBER"
    print("Clicking phone login...")
    page.click('text=LOG IN BY PHONE NUMBER')
    time.sleep(3)
    
    # Enter phone number
    print(f"Entering phone: {PHONE}")
    page.fill('input[type="tel"]', PHONE)
    time.sleep(2)
    
    # Click Next/Continue
    page.click('button:has-text("Next"), .btn-primary, button[type="submit"]')
    time.sleep(5)
    
    # Screenshot to see current state
    page.screenshot(path='/home/chad-yi/.openclaw/workspace/telegram_phone_entry.png')
    print("Screenshot saved: telegram_phone_entry.png")
    print("Check if it asks for SMS code...")
    
    content = page.content()
    if "code" in content.lower() or "sms" in content.lower():
        print("✅ Ready for SMS code!")
        print("Enter the code you receive on your phone:")
        
        # Wait for manual input (in real scenario)
        # code = input("SMS Code: ")
        # page.fill('input[type="number"]', code)
        # page.click('button:has-text("Next")')
    else:
        print("Current page state:")
        print(content[:500])
    
    browser.close()