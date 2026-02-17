#!/usr/bin/env python3
"""
Telegram Monitor for Kimi-Claw-Helios
Checks CallistoFX every 2 minutes for trading signals
"""

from playwright.sync_api import sync_playwright
import json
import re
from datetime import datetime
from pathlib import Path

# Config
CHAD_YI_TELEGRAM = "512366713"
SIGNALS_DIR = Path("~/signals").expanduser()
SIGNALS_DIR.mkdir(exist_ok=True)

def parse_signal(text):
    """Extract trading signal from message"""
    up = text.upper()
    
    if 'BUY' not in up and 'SELL' not in up:
        return None
    
    symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    symbol = next((s for s in symbols if s in up), None)
    
    if not symbol:
        return None
    
    direction = 'BUY' if 'BUY' in up else 'SELL'
    
    # Entry
    range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
    entry = range_match.groups() if range_match else None
    
    # SL
    sl_match = re.search(r'SL[:\s]*(\d+\.?\d*)', up)
    sl = sl_match.group(1) if sl_match else None
    
    # TPs
    tps = re.findall(r'(?:TP\d*[:\s]*)(\d+\.?\d*)', up)
    
    return {
        'symbol': symbol,
        'direction': direction,
        'entry': entry,
        'sl': sl,
        'tps': tps,
        'raw': text[:200]
    }

def alert_chad_yi(signal, screenshot_path):
    """Send alert to CHAD_YI"""
    msg = f"""🚨 TRADING SIGNAL DETECTED

Time: {datetime.now().strftime('%H:%M:%S')}

Signal:
{signal['symbol']} {signal['direction']}
Entry: {signal['entry']}
SL: {signal['sl']}
TP: {signal['tps']}

Screenshot: {screenshot_path}

[CHAD_YI: Execute trade?]
"""
    
    # Use OpenClaw messaging to send to CHAD_YI
    print(msg)
    # In real implementation: message.send(to=CHAD_YI_TELEGRAM, text=msg, media=screenshot_path)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to Telegram Web (assume already logged in)
        page.goto("https://web.telegram.org/a/")
        page.wait_for_timeout(5000)
        
        # Navigate to CallistoFX (need to find channel)
        # This assumes channel is in recent chats
        # In practice: click on CallistoFX from sidebar
        
        # For now: screenshot current view
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = SIGNALS_DIR / f"telegram_{timestamp}.png"
        page.screenshot(path=str(screenshot_path))
        
        # Get page content
        content = page.content()
        
        # Look for signal patterns
        # This is simplified - real implementation needs proper selectors
        
        browser.close()
        
        print(f"Screenshot saved: {screenshot_path}")

if __name__ == '__main__':
    main()