#!/usr/bin/env python3
"""
QUANTA TRADER - Automated Trading Agent
Local Ollama model (zero token cost)
Reads Telegram signals → Executes OANDA trades
"""

import pytesseract
from PIL import ImageGrab
import pyautogui
import requests
import json
import re
import time
from datetime import datetime
from pathlib import Path
import logging

# Configuration
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")
LOG_FILE = Path("C:/DesktopControlAgent/logs/quanta_trades.log")

# Account Settings
ACCOUNT_BALANCE = 2000  # USD
RISK_PERCENT = 2  # 2% per trade
MAX_RISK_USD = ACCOUNT_BALANCE * (RISK_PERCENT / 100)  # $40

# OANDA Settings (to be filled)
OANDA_API_KEY = "YOUR_API_KEY_HERE"
OANDA_ACCOUNT_ID = "YOUR_ACCOUNT_ID_HERE"
OANDA_API_URL = "https://api-fxpractice.oanda.com"  # Practice account

# Telegram/CallistoFx monitoring
CHANNEL_NAME = "CallistoFx Premium Channel"
CHECK_INTERVAL = 1  # seconds (was 10, now 1 for speed)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuantaTrader:
    def __init__(self):
        self.last_signal = None
        self.active_trades = []
        
    def take_screenshot(self):
        """Take screenshot of screen"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = SCREENSHOT_DIR / f"quanta_scan_{timestamp}.png"
            screenshot.save(filename)
            return screenshot, filename
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None, None
    
    def read_screen(self, screenshot):
        """OCR read text from screenshot"""
        try:
            text = pytesseract.image_to_string(screenshot)
            return text
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def parse_signal(self, text):
        """Parse trading signal from text"""
        signal = {}
        
        # Look for symbol
        symbol_match = re.search(r'(XAUUSD|XAGUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|USDCAD|GBPJPY)', text, re.IGNORECASE)
        if symbol_match:
            signal['symbol'] = symbol_match.group(1).upper()
        
        # Look for direction
        direction_match = re.search(r'\b(BUY|SELL)\b', text, re.IGNORECASE)
        if direction_match:
            signal['direction'] = direction_match.group(1).upper()
        
        # Look for entry range
        entry_match = re.search(r'(?:Buy|Sell)\s*Range[:\s]+(\d+\.?\d*)\s*[-~to]+\s*(\d+\.?\d*)', text, re.IGNORECASE)
        if entry_match:
            signal['entry_high'] = float(entry_match.group(1))
            signal['entry_low'] = float(entry_match.group(2))
        
        # Look for SL
        sl_match = re.search(r'SL[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        if sl_match:
            signal['sl'] = float(sl_match.group(1))
        
        # Look for TPs
        tp_match = re.search(r'TP[:\s]+([\d\s/.]+)', text, re.IGNORECASE)
        if tp_match:
            tp_text = tp_match.group(1)
            tps = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
            signal['tps'] = tps
        
        # Validate signal
        if all(k in signal for k in ['symbol', 'direction', 'entry_high', 'entry_low', 'sl', 'tps']):
            return signal
        
        return None
    
    def calculate_split_entries(self, signal):
        """Calculate 3 split entries with position sizing"""
        entry_high = signal['entry_high']
        entry_low = signal['entry_low']
        entry_mid = (entry_high + entry_low) / 2
        sl = signal['sl']
        direction = signal['direction']
        
        # Calculate pips risk for each entry
        if direction == "BUY":
            risk_high = entry_high - sl
            risk_mid = entry_mid - sl
            risk_low = entry_low - sl
        else:  # SELL
            risk_high = sl - entry_low
            risk_mid = sl - entry_mid
            risk_low = sl - entry_high
        
        # Size each entry: risk $13.33 each (total $40)
        risk_per_entry = MAX_RISK_USD / 3
        
        entries = [
            {'price': entry_high, 'risk_pips': risk_high, 'size': 0, 'risk_usd': 0},
            {'price': entry_mid, 'risk_pips': risk_mid, 'size': 0, 'risk_usd': 0},
            {'price': entry_low, 'risk_pips': risk_low, 'size': 0, 'risk_usd': 0}
        ]
        
        # Calculate size for each (1 pip = $0.01 per 0.01 lot for XAUUSD)
        for entry in entries:
            if entry['risk_pips'] > 0:
                # For XAUUSD: 1 pip = $0.01 per 0.01 lot
                # Size in lots = Risk USD / (Risk Pips * $0.01 * 100)
                entry['size'] = round(risk_per_entry / (entry['risk_pips'] * 1), 2)
                entry['risk_usd'] = entry['size'] * entry['risk_pips']
        
        total_risk = sum(e['risk_usd'] for e in entries)
        
        return {
            'entries': entries,
            'total_risk': total_risk,
            'avg_entry': sum(e['price'] for e in entries) / 3
        }
    
    def execute_trade_oanda(self, signal, split_entries):
        """Execute trade via OANDA API"""
        logger.info(f"Executing trade: {signal}")
        logger.info(f"Split entries: {split_entries}")
        
        # This is where OANDA API calls would go
        # For now, log the intended trades
        for i, entry in enumerate(split_entries['entries'], 1):
            logger.info(f"Entry {i}: {entry['price']} @ {entry['size']} lots, Risk: ${entry['risk_usd']:.2f}")
        
        logger.info(f"SL: {signal['sl']}")
        logger.info(f"TPs: {signal['tps']}")
        logger.info(f"Total Risk: ${split_entries['total_risk']:.2f}")
        
        # TODO: Implement actual OANDA API calls
        # For now, simulate
        return True
    
    def check_tp_and_move_sl(self, signal, entry_price):
        """Check if TP1 hit, move SL to breakeven"""
        # TODO: Monitor trade and move SL when TP1 hit
        pass
    
    def run(self):
        """Main loop - scan for signals every 1 second"""
        logger.info("="*60)
        logger.info("QUANTA TRADER STARTED")
        logger.info(f"Account: ${ACCOUNT_BALANCE}")
        logger.info(f"Max Risk: ${MAX_RISK_USD}")
        logger.info(f"Scan interval: {CHECK_INTERVAL}s")
        logger.info("="*60)
        
        print("Quanta Trader is running...")
        print(f"Scanning every {CHECK_INTERVAL} second(s) for signals...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Take screenshot
                screenshot, filename = self.take_screenshot()
                
                if screenshot:
                    # Read text
                    text = self.read_screen(screenshot)
                    
                    # Check for signal
                    signal = self.parse_signal(text)
                    
                    if signal and signal != self.last_signal:
                        logger.info(f"NEW SIGNAL DETECTED: {signal}")
                        print(f"\n🎯 SIGNAL: {signal['symbol']} {signal['direction']}")
                        print(f"Range: {signal['entry_high']} - {signal['entry_low']}")
                        print(f"SL: {signal['sl']}")
                        print(f"TPs: {signal['tps']}")
                        
                        # Calculate split entries
                        split_entries = self.calculate_split_entries(signal)
                        
                        # Execute trade
                        if self.execute_trade_oanda(signal, split_entries):
                            self.last_signal = signal
                            self.active_trades.append({
                                'signal': signal,
                                'entries': split_entries,
                                'time': datetime.now()
                            })
                            print("✅ Trade executed!")
                        else:
                            print("❌ Trade failed")
                
                # Wait before next scan
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Quanta Trader stopped by user")
            print("\nStopped.")

if __name__ == "__main__":
    trader = QuantaTrader()
    trader.run()
