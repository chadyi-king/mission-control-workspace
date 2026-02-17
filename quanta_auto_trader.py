#!/usr/bin/env python3
"""
Quanta Auto-Trader - Telegram Web + OANDA
Monitors Telegram Web continuously, auto-executes trades
"""

from playwright.sync_api import sync_playwright
import time
import json
import re
from datetime import datetime
import sys
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from oanda_executor import OandaExecutor

class QuantaAutoTrader:
    def __init__(self):
        self.browser = None
        self.page = None
        self.executor = OandaExecutor()
        self.channel_url = None
        self.last_message = ""
        
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] {msg}")
        
    def parse_signal(self, text):
        """Parse signal from message text"""
        text_upper = text.upper()
        
        if 'BUY' not in text_upper and 'SELL' not in text_upper:
            return None
        
        symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
        symbol = None
        for sym in symbols:
            if sym in text_upper:
                symbol = sym
                break
        
        if not symbol:
            return None
        
        direction = 'BUY' if 'BUY' in text_upper else 'SELL'
        
        # Parse entry range
        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
        entry = None
        if range_match:
            entry = (float(range_match.group(1)), float(range_match.group(2)))
        
        # Parse SL
        sl_match = re.search(r'SL[:\s]*(\d+\.?\d*)', text_upper)
        sl = float(sl_match.group(1)) if sl_match else None
        
        # Parse TPs
        tp_matches = re.findall(r'(?:TP\d*[:\s]*|Target[:\s]*)(\d+\.?\d*)', text_upper)
        tps = [float(tp) for tp in tp_matches] if tp_matches else []
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry': entry,
            'sl': sl,
            'tps': tps,
            'raw': text[:200]
        }
    
    def execute_trade(self, signal):
        """Execute trade via OANDA"""
        self.log(f"🚨 EXECUTING: {signal['symbol']} {signal['direction']}")
        
        # Get current price
        instrument = signal['symbol'].replace('USD', '_USD')
        if instrument.startswith('USD'):
            instrument = instrument.replace('_USD', 'USD_')
        
        price_data = self.executor.get_price(instrument)
        if not price_data['success']:
            self.log(f"❌ Failed to get price: {price_data}")
            return False
        
        current_price = price_data['ask'] if signal['direction'] == 'BUY' else price_data['bid']
        self.log(f"   Current price: {current_price}")
        
        # Check if entry is valid
        if signal['entry']:
            entry_low, entry_high = signal['entry']
            if entry_low <= current_price <= entry_high:
                self.log(f"   ✅ Price within entry zone!")
            else:
                self.log(f"   ⚠️ Price outside entry zone ({entry_low}-{entry_high})")
                if signal['direction'] == 'BUY' and current_price > entry_high:
                    self.log(f"   Price above entry - market order")
                elif signal['direction'] == 'SELL' and current_price < entry_low:
                    self.log(f"   Price below entry - market order")
                else:
                    self.log(f"   Skipping - too far from entry")
                    return False
        
        # Calculate position size ($20 risk) - CORRECTED
        if signal['sl']:
            sl_distance = abs(current_price - signal['sl'])
            if sl_distance > 0:
                # For XAUUSD: $0.01 per pip per unit
                # Risk = SL_distance × units × $0.01
                # units = $20 / (SL_distance × $0.01)
                units = 20 / (sl_distance * 0.01)
                units = int(units)
                # Cap at safe levels for $2000 account
                if units > 100:  # Max 100 units (~$500 margin)
                    units = 100
                if units < 10:
                    units = 10  # Min 10 units
            else:
                units = 20  # Safe default
        else:
            units = 20  # Safe default without SL
        
        self.log(f"   Position: {units} units (~${units * 5} margin needed)")
        
        # Place order
        result = self.executor.create_order(
            instrument=instrument,
            direction=signal['direction'],
            units=units,
            stop_loss=signal['sl'],
            take_profit=signal['tps'][0] if signal['tps'] else None
        )
        
        if result['success']:
            self.log(f"✅ Trade executed! Order ID: {result.get('order_id', 'N/A')}")
            return True
        else:
            self.log(f"❌ Trade failed: {result}")
            return False
    
    def run(self):
        """Main loop - monitor and trade"""
        self.log("=" * 50)
        self.log("Quanta Auto-Trader Starting")
        self.log("=" * 50)
        
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            
            self.log("Opening Telegram Web...")
            self.page.goto("https://web.telegram.org")
            
            self.log("Waiting for login... (you need to be already logged in)")
            time.sleep(10)
            
            # Check if logged in
            if "Log in" in self.page.content() or "QR Code" in self.page.content():
                self.log("❌ Not logged in! Please log in first.")
                self.browser.close()
                return
            
            self.log("✅ Logged in!")
            
            # Navigate to CallistoFX channel
            self.log("Looking for CallistoFX channel...")
            # Wait for chat list to load
            time.sleep(5)
            
            # Try to find and click on CallistoFX
            try:
                # Look for channel in sidebar
                channel_selector = 'text=CallistoFX'
                if self.page.locator(channel_selector).count() > 0:
                    self.page.locator(channel_selector).first.click()
                    self.log("✅ Opened CallistoFX channel")
                    time.sleep(3)
                else:
                    self.log("⚠️ CallistoFX not found in sidebar")
                    self.log("Please navigate to the channel manually in the browser")
            except Exception as e:
                self.log(f"⚠️ Could not find channel: {e}")
            
            self.log("✅ Monitoring for signals...")
            
            # Monitor loop
            while True:
                try:
                    # Get latest message
                    # Telegram Web messages have specific selectors
                    message_selector = '.message-content, .message-text'
                    messages = self.page.locator(message_selector).all_inner_texts()
                    
                    if messages:
                        latest = messages[-1].strip()
                        
                        if latest != self.last_message:
                            self.last_message = latest
                            self.log(f"💬 New message: {latest[:50]}...")
                            
                            # Parse signal
                            signal = self.parse_signal(latest)
                            if signal:
                                self.log(f"🚨 SIGNAL DETECTED: {signal['symbol']} {signal['direction']}")
                                self.execute_trade(signal)
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    self.log(f"Error: {e}")
                    time.sleep(5)
    
    def stop(self):
        if self.browser:
            self.browser.close()
        self.log("Stopped")

if __name__ == '__main__':
    trader = QuantaAutoTrader()
    try:
        trader.run()
    except KeyboardInterrupt:
        trader.stop()