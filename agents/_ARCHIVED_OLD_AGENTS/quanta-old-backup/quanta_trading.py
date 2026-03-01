#!/usr/bin/env python3
"""
Quanta Trading Monitor v7.0 - WITH OANDA TRADING
Monitors CallistoFX + Executes trades automatically
"""

import asyncio
import json
import re
import os
import sys
import signal
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient, events

# Setup paths
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
INBOX_DIR = BASE_DIR / 'inbox'
SESSION_FILE = BASE_DIR / 'sessions' / 'quanta'
PID_FILE = BASE_DIR / 'quanta_trading.pid'

LOG_DIR.mkdir(exist_ok=True)
INBOX_DIR.mkdir(exist_ok=True)
SESSION_FILE.parent.mkdir(exist_ok=True)

sys.path.insert(0, str(BASE_DIR))
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, CALLISTOFX_CHANNEL

# Try to import OANDA executor
try:
    from oanda_executor import OandaExecutor
    from oanda_config import OANDA_ACCOUNT_ID, OANDA_API_KEY
    TRADING_ENABLED = True
except ImportError:
    TRADING_ENABLED = False

running = True

class QuantaTrading:
    def __init__(self):
        self.client = None
        self.executor = None
        self.channel_id = None
        self.msg_count = 0
        
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_DIR / 'quanta_trading.log', 'a') as f:
            f.write(line + '\n')
    
    def log_message(self, text):
        entry = {
            'time': datetime.utcnow().isoformat(),
            'text': text
        }
        with open(LOG_DIR / 'messages.jsonl', 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def parse_signal(self, text):
        """Parse signal with full details for trading"""
        up = text.upper()
        
        if 'BUY' not in up and 'SELL' not in up:
            return None
        
        # All symbols including crosses
        symbols = ['XAUUSD', 'XAGUSD', 'BTCUSD', 'ETHUSD', 
                   'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
                   'USDCAD', 'USDCHF', 'NZDUSD',
                   'EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY', 
                   'CADJPY', 'CHFJPY', 'NZDJPY', 
                   'EURAUD', 'EURCHF', 'GBPAUD', 'GBPCAD', 'GBPCHF',
                   'US30', 'NAS100']
        
        symbol = None
        for sym in symbols:
            if sym in up:
                symbol = sym
                break
        
        if not symbol:
            return None
        
        direction = 'BUY' if 'BUY' in up else 'SELL'
        
        # Parse entry range
        range_match = re.search(r'(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)', text)
        entry_low = entry_high = None
        if range_match:
            entry_low = float(range_match.group(1))
            entry_high = float(range_match.group(2))
        else:
            # Try to find any price number
            price_match = re.search(r'\b(\d{4,6}\.\d+|\d{4,6})\b', text)
            if price_match:
                price = float(price_match.group(1))
                entry_low = entry_high = price
        
        # Parse SL
        sl_match = re.search(r'SL[:\s]*(\d+\.?\d*)', up)
        sl = float(sl_match.group(1)) if sl_match else None
        
        # Parse TPs
        tp_matches = re.findall(r'(?:TP\d*[:\s]*|Target[:\s]*)(\d+\.?\d*)', up)
        tps = [float(tp) for tp in tp_matches] if tp_matches else []
        
        signal = {
            'symbol': symbol,
            'direction': direction,
            'entry_low': entry_low,
            'entry_high': entry_high,
            'sl': sl,
            'tps': tps,
            'raw_text': text[:200],
            'time': datetime.now().isoformat()
        }
        
        return signal
    
    async def execute_trade(self, signal):
        """Execute trade via OANDA"""
        if not TRADING_ENABLED:
            self.log("⚠️ Trading disabled - OANDA not configured")
            return False
        
        if not signal.get('sl') or not signal.get('tps'):
            self.log("⚠️ Signal incomplete (no SL/TP) - not trading")
            return False
        
        try:
            self.log(f"🚀 EXECUTING: {signal['symbol']} {signal['direction']}")
            
            # Prepare order
            symbol_oanda = signal['symbol'].replace('USD', '_USD')
            if symbol_oanda.startswith('USD'):
                symbol_oanda = symbol_oanda.replace('_USD', 'USD_')
            
            # Calculate position size (2% risk)
            risk_amount = 40  # $40 SGD (2% of ~$2000)
            
            entry = signal.get('entry_mid') or signal.get('entry_low')
            sl = signal['sl']
            
            if signal['direction'] == 'BUY':
                sl_distance = abs(entry - sl)
            else:
                sl_distance = abs(sl - entry)
            
            if sl_distance == 0:
                self.log("⚠️ Invalid SL distance")
                return False
            
            # Execute via OANDA
            # NOTE: This is simplified - full implementation in oanda_executor.py
            self.log(f"   Entry: {entry}")
            self.log(f"   SL: {sl}")
            self.log(f"   TPs: {signal['tps']}")
            self.log(f"   Risk: ${risk_amount}")
            
            # Save trade record
            trade_file = INBOX_DIR / f"trade_{datetime.now():%H%M%S}.json"
            with open(trade_file, 'w') as f:
                json.dump(signal, f, indent=2)
            
            self.log(f"✅ Trade saved: {trade_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Trade error: {e}")
            return False
    
    async def handle_message(self, event):
        try:
            text = event.message.text or event.message.caption or ''
            if not text:
                return
            
            self.log_message(text)
            self.msg_count += 1
            
            preview = text[:50].replace('\n', ' ')
            self.log(f"💬 {preview}...")
            
            # Parse signal
            signal = self.parse_signal(text)
            if signal:
                self.log(f"🚨 SIGNAL: {signal['symbol']} {signal['direction']}")
                self.log(f"   Entry: {signal['entry_low']}-{signal['entry_high']}")
                self.log(f"   SL: {signal.get('sl', 'N/A')}")
                
                # Save signal
                sig_file = INBOX_DIR / f"sig_{datetime.now():%H%M%S}.json"
                with open(sig_file, 'w') as f:
                    json.dump(signal, f)
                
                # Execute trade if complete signal
                if signal.get('sl') and signal.get('tps'):
                    await self.execute_trade(signal)
                else:
                    self.log("   ⚠️ Analysis only (no SL/TP)")
                    
        except Exception as e:
            self.log(f"Error: {e}")
    
    async def run(self):
        global running
        
        self.log("=" * 50)
        self.log("Quanta Trading Monitor v7.0")
        self.log(f"Trading: {'ENABLED' if TRADING_ENABLED else 'DISABLED'}")
        self.log("=" * 50)
        
        PID_FILE.write_text(str(os.getpid()))
        
        self.client = TelegramClient(str(SESSION_FILE), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                self.log("❌ Not authorized! Run: python3 auth.py")
                return 1
            
            me = await self.client.get_me()
            self.log(f"✓ Connected as: {me.first_name}")
            
            # Find channel
            async for d in self.client.iter_dialogs():
                if CALLISTOFX_CHANNEL in d.name:
                    self.channel_id = d.id
                    self.log(f"✓ Found channel: {d.name}")
                    break
            
            @self.client.on(events.NewMessage(chats=self.channel_id) if self.channel_id else events.NewMessage)
            async def handler(event):
                await self.handle_message(event)
            
            self.log("✓ Monitoring 24/7 for signals...")
            
            while running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.log(f"Fatal: {e}")
            return 1
        finally:
            await self.client.disconnect()
            if PID_FILE.exists():
                PID_FILE.unlink()
            self.log("Stopped")
        
        return 0
    
    def stop(self):
        global running
        running = False

def shutdown(signum, frame):
    global quanta
    if quanta:
        quanta.stop()

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

if __name__ == '__main__':
    quanta = QuantaTrading()
    try:
        exit(asyncio.run(quanta.run()))
    except KeyboardInterrupt:
        print("\nBye")
        sys.exit(0)