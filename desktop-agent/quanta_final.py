#!/usr/bin/env python3
"""
QUANTA - Automated Trading Agent
Uses: LLaVA (vision) + CodeLlama (brain) + OANDA API
Account: $2,000 | Risk: 2% per trade | Local models (zero tokens)
"""

import ollama
import pytesseract
from PIL import Image, ImageGrab
import pyautogui
import json
import re
import time
from datetime import datetime
from pathlib import Path
import logging
import requests

# Setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
SCREENSHOT_DIR = Path("C:/DesktopControlAgent/quanta_screenshots")
LOG_FILE = Path("C:/DesktopControlAgent/logs/quanta.log")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Account Config
CONFIG = {
    "balance": 2000,           # Starting balance
    "risk_percent": 2,         # 2% per trade
    "mode": "PAPER",           # "PAPER" or "LIVE"
    
    # OANDA (fill in when ready)
    "oanda_api_key": "YOUR_API_KEY",
    "oanda_account_id": "YOUR_ACCOUNT_ID",
    "oanda_url": "https://api-fxpractice.oanda.com",
    
    # Models
    "vision_model": "llava:13b",      # For reading screenshots
    "brain_model": "codellama:7b",    # For trading decisions
    
    # Settings
    "screenshot_interval": 2,   # Seconds
    "channel": "CallistoFx Premium Channel",
    "validation_required": False,  # AUTO-TRADE MODE (testing phase)
    "test_mode": True,          # First 20 trades = $2 each
    "test_trade_count": 0,      # Counter
    "max_test_trades": 20,      # After 20, review performance
    "test_trade_size": 2        # $2 per trade for testing
}

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantaTrader:
    def __init__(self):
        self.balance = CONFIG["balance"]
        self.active_trades = []
        self.trade_history = []
        logger.info("Quanta initialized")
    
    def take_screenshot(self):
        """Capture screen"""
        try:
            img = ImageGrab.grab()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SCREENSHOT_DIR / f"scan_{timestamp}.png"
            img.save(path)
            return img, path
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None, None
    
    def read_with_llava(self, image_path):
        """Use LLaVA to read screenshot"""
        try:
            # Convert image to base64
            with open(image_path, "rb") as f:
                img_base64 = f.read()
            
            # Ask LLaVA to extract trading signal
            response = ollama.generate(
                model=CONFIG["vision_model"],
                prompt="""Extract any trading signal from this screenshot.
                Look for:
                - Symbol (XAUUSD, EURUSD, etc.)
                - Direction (BUY or SELL)
                - Entry range (e.g., 2685-2675)
                - SL price
                - TP targets (list of prices)
                
                Return as JSON:
                {"signal": true/false, "symbol": "", "direction": "", "entry_high": 0, "entry_low": 0, "sl": 0, "tps": []}
                If no signal, return {"signal": false}""",
                images=[img_base64]
            )
            
            # Parse response
            text = response['response']
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"signal": False}
            
        except Exception as e:
            logger.error(f"LLaVA failed: {e}")
            # Fallback to Tesseract
            return self.read_with_tesseract(image_path)
    
    def read_with_tesseract(self, image_path):
        """Backup: Use Tesseract OCR"""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            
            # Parse with regex
            signal = {"signal": False}
            
            if "XAUUSD" in text and ("BUY" in text or "SELL" in text):
                signal["signal"] = True
                signal["symbol"] = "XAUUSD"
                
                direction = re.search(r'(BUY|SELL)', text)
                if direction:
                    signal["direction"] = direction.group(1)
                
                entry = re.search(r'Range[:\s]+(\d+\.?\d*)\s*[-~]+\s*(\d+\.?\d*)', text)
                if entry:
                    signal["entry_high"] = float(entry.group(1))
                    signal["entry_low"] = float(entry.group(2))
                
                sl = re.search(r'SL[:\s]+(\d+\.?\d*)', text)
                if sl:
                    signal["sl"] = float(sl.group(1))
                
                tps = re.findall(r'\d+\.?\d*', re.search(r'TP[:\s]+([\d\s/.]+)', text).group(1) if re.search(r'TP[:\s]+([\d\s/.]+)', text) else "")
                signal["tps"] = [float(x) for x in tps[:5]]
            
            return signal
            
        except Exception as e:
            logger.error(f"Tesseract failed: {e}")
            return {"signal": False}
    
    def create_trading_plan(self, signal):
        """Use CodeLlama to create trading plan"""
        
        risk_amount = self.balance * (CONFIG["risk_percent"] / 100)
        
        prompt = f"""You are a trading expert. Create a trading plan for this signal.
        
        Signal: {signal['symbol']} {signal['direction']}
        Entry Range: {signal['entry_high']} - {signal['entry_low']}
        SL: {signal['sl']}
        TPs: {signal['tps']}
        Account Balance: ${self.balance}
        Max Risk: ${risk_amount}
        
        Calculate:
        1. Split into 3 entries (high, mid, low of range)
        2. Lot size for each entry (risk $13.33 each, total $40)
        3. TP ladder (close % at each TP)
        4. Breakeven rule
        
        Return JSON:
        {{
            "entry_1": {{"price": 0, "size": 0, "risk": 0}},
            "entry_2": {{"price": 0, "size": 0, "risk": 0}},
            "entry_3": {{"price": 0, "size": 0, "risk": 0}},
            "total_risk": 0,
            "tp_strategy": "10% at TP1, 10% at TP2, 20% at TP3, 30% at TP4, 30% runner",
            "breakeven_rule": "Move SL to entry when TP1 hits"
        }}"""
        
        try:
            response = ollama.generate(
                model=CONFIG["brain_model"],
                prompt=prompt
            )
            
            text = response['response']
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"CodeLlama failed: {e}")
        
        # Fallback calculation
        return self.calculate_plan_manually(signal, risk_amount)
    
    def calculate_plan_manually(self, signal, risk_amount):
        """Manual calculation if LLM fails"""
        entry_high = signal["entry_high"]
        entry_low = signal["entry_low"]
        entry_mid = (entry_high + entry_low) / 2
        
        risk_per_entry = risk_amount / 3
        
        # Calculate sizes (simplified for XAUUSD)
        # 1 pip = $0.01 per 0.01 lot
        risk_pips_high = entry_high - signal["sl"]
        risk_pips_mid = entry_mid - signal["sl"]
        risk_pips_low = entry_low - signal["sl"]
        
        return {
            "entry_1": {"price": entry_high, "size": round(risk_per_entry / risk_pips_high, 2) if risk_pips_high > 0 else 0, "risk": risk_per_entry},
            "entry_2": {"price": entry_mid, "size": round(risk_per_entry / risk_pips_mid, 2) if risk_pips_mid > 0 else 0, "risk": risk_per_entry},
            "entry_3": {"price": entry_low, "size": round(risk_per_entry / risk_pips_low, 2) if risk_pips_low > 0 else 0, "risk": risk_per_entry},
            "total_risk": risk_amount,
            "tp_strategy": "10% TP1, 10% TP2, 20% TP3, 30% TP4, 30% runner",
            "breakeven_rule": "Move SL to entry when TP1 hits"
        }
    
    def present_plan(self, signal, plan):
        """Show trading plan to user for approval"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    TRADE PROPOSAL                            ║
╚══════════════════════════════════════════════════════════════╝

SIGNAL DETECTED:
  Symbol: {signal['symbol']}
  Direction: {signal['direction']}
  Entry Range: {signal['entry_high']} - {signal['entry_low']}
  SL: {signal['sl']}
  TPs: {signal['tps']}

EXECUTION PLAN:
  Entry 1 (High): {plan['entry_1']['price']} @ {plan['entry_1']['size']} lots
  Entry 2 (Mid):  {plan['entry_2']['price']} @ {plan['entry_2']['size']} lots
  Entry 3 (Low):  {plan['entry_3']['price']} @ {plan['entry_3']['size']} lots

RISK MANAGEMENT:
  Total Risk: ${plan['total_risk']:.2f} (2% of balance)
  Risk per Entry: ~${plan['entry_1']['risk']:.2f}
  
EXIT STRATEGY:
  {plan['tp_strategy']}
  Breakeven: {plan['breakeven_rule']}

Account Balance: ${self.balance}
Mode: {CONFIG['mode']}

╔══════════════════════════════════════════════════════════════╗
║  APPROVE TRADE? (Type: YES / NO / MODIFY)                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(report)
        return report
    
    def execute_paper_trade(self, signal, plan):
        """Simulate trade (no real money)"""
        self.test_trade_count += 1
        
        trade = {
            "id": self.test_trade_count,
            "signal": signal,
            "plan": plan,
            "status": "OPEN",
            "opened_at": datetime.now(),
            "pnl": 0,
            "mode": "TEST" if self.test_trade_count <= 20 else "FULL",
            "test_size": CONFIG["test_trade_size"] if self.test_trade_count <= 20 else "2% risk"
        }
        self.active_trades.append(trade)
        self.trade_history.append(trade)
        
        # Log with test info
        mode_str = f"TEST #{self.test_trade_count}/20 ($2)" if self.test_trade_count <= 20 else f"TRADE #{self.test_trade_count}"
        logger.info(f"{mode_str}: {signal}")
        
        print(f"\n{'='*60}")
        print(f"✅ AUTO-TRADE EXECUTED: {mode_str}")
        print(f"Symbol: {signal['symbol']} {signal['direction']}")
        print(f"Entries: {plan['entry_1']['price']}, {plan['entry_2']['price']}, {plan['entry_3']['price']}")
        print(f"Risk: ${plan['total_risk']:.2f}")
        if self.test_trade_count <= 20:
            print(f"TEST MODE: Using $2 size (trade {self.test_trade_count}/20)")
        print(f"{'='*60}\n")
        
        return trade
    
    def execute_live_trade(self, signal, plan):
        """Execute real trade on OANDA"""
        # TODO: Implement OANDA API calls
        print("⚠️  LIVE TRADE - OANDA API not yet configured")
        print("Update CONFIG['oanda_api_key'] to enable")
        return None
    
    def run(self):
        """Main loop"""
        print("=" * 60)
        print("QUANTA TRADER STARTED")
        print(f"Mode: {CONFIG['mode']}")
        print(f"Balance: ${CONFIG['balance']}")
        print(f"Risk: {CONFIG['risk_percent']}% per trade")
        print(f"Scanning every {CONFIG['screenshot_interval']} seconds")
        print("=" * 60)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                # Take screenshot
                img, path = self.take_screenshot()
                if img:
                    # Read with LLaVA
                    signal = self.read_with_llava(path)
                    
                    if signal.get("signal"):
                        print(f"\n🎯 SIGNAL DETECTED: {signal}")
                        
                        # Create plan
                        plan = self.create_trading_plan(signal)
                        
                        # Present for approval
                        self.present_plan(signal, plan)
                        
                        # Present for approval (or auto-execute in test mode)
                        if CONFIG["test_mode"] and self.test_trade_count < CONFIG["max_test_trades"]:
                            print("🧪 TEST MODE: Auto-executing (no approval needed)")
                            approval = "YES"
                            time.sleep(2)  # Brief pause so you can see it
                        elif CONFIG["validation_required"]:
                            approval = input("\nYour decision: ").strip().upper()
                        else:
                            approval = "YES"
                        
                        if approval == "YES":
                            if CONFIG["mode"] == "PAPER":
                                self.execute_paper_trade(signal, plan)
                            else:
                                self.execute_live_trade(signal, plan)
                        elif approval == "NO":
                            print("❌ Trade rejected")
                        else:
                            print("⚠️  Modify not yet implemented")
                    else:
                        print(".", end="", flush=True)  # No signal
                
                time.sleep(CONFIG["screenshot_interval"])
                
        except KeyboardInterrupt:
            print("\n\nQuanta stopped.")
            print(f"Total trades: {len(self.trade_history)}")
            print(f"Test trades: {min(self.test_trade_count, 20)}/20")
            if self.test_trade_count >= 20:
                print("✅ Test phase complete! Review performance before full trading.")

if __name__ == "__main__":
    print("Starting Quanta...")
    print("Note: First scan may take 10-20 seconds to load models")
    quanta = QuantaTrader()
    quanta.run()
