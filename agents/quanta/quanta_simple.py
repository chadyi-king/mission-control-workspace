#!/usr/bin/env python3
"""
Quanta - SIMPLE VERSION THAT ACTUALLY WORKS
Telegram + OANDA trading
"""

import asyncio
import json
import re
import os
import sys
from datetime import datetime
from pathlib import Path

# Add paths
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, CALLISTOFX_CHANNEL
from oanda_executor import OandaExecutor
from telethon import TelegramClient, events

BASE_DIR = Path('/home/chad-yi/.openclaw/workspace/agents/quanta')
LOG_DIR = BASE_DIR / 'logs'
INBOX_DIR = BASE_DIR / 'inbox'
SESSION_FILE = BASE_DIR / 'sessions' / 'quanta'
PID_FILE = BASE_DIR / 'quanta.pid'

LOG_DIR.mkdir(exist_ok=True)
INBOX_DIR.mkdir(exist_ok=True)

class SimpleQuanta:
    def __init__(self):
        self.client = None
        self.executor = OandaExecutor()
        self.running = True
        
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_DIR / 'simple.log', 'a') as f:
            f.write(line + '\n')
    
    def save_signal(self, signal):
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            **signal
        }
        with open(INBOX_DIR / f"sig_{datetime.now():%H%M%S}.json", 'w') as f:
            json.dump(entry, f)
    
    def parse_signal(self, text):
        up = text.upper()
        if 'BUY' not in up and 'SELL' not in up:
            return None
        
        symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY',
                   'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']
        
        symbol = None
        for sym in symbols:
            if sym in up:
                symbol = sym
                break
        
        if not symbol:
            return None
        
        direction = 'BUY' if 'BUY' in up else 'SELL'
        
        # Entry range
        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
        entry = None
        if range_match:
            entry = (float(range_match.group(1)), float(range_match.group(2)))
        
        # SL
        sl_match = re.search(r'SL[:\s]*(\d+\.?\d*)', up)
        sl = float(sl_match.group(1)) if sl_match else None
        
        # TPs
        tp_matches = re.findall(r'(?:TP\d*[:\s]*|Target[:\s]*)(\d+\.?\d*)', up)
        tps = [float(tp) for tp in tp_matches] if tp_matches else []
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry': entry,
            'sl': sl,
            'tps': tps,
            'raw': text[:200]
        }
    
    async def execute_trade(self, signal):
        """Execute trade with proper sizing"""
        self.log(f"🚨 EXECUTING: {signal['symbol']} {signal['direction']}")
        
        # Get current price
        instrument = signal['symbol'].replace('USD', '_USD')
        price_data = self.executor.get_price(instrument)
        
        if not price_data['success']:
            self.log(f"❌ Price error: {price_data}")
            return False
        
        current = price_data['ask'] if signal['direction'] == 'BUY' else price_data['bid']
        self.log(f"   Price: {current}")
        
        # Calculate units ($20 risk max)
        if signal['sl']:
            sl_dist = abs(current - signal['sl'])
            if sl_dist > 0:
                units = int(20 / (sl_dist * 0.01))  # XAUUSD: $0.01/pip/unit
                units = max(10, min(units, 100))  # Cap 10-100 units
            else:
                units = 20
        else:
            units = 20
        
        self.log(f"   Units: {units}")
        
        # Execute
        result = self.executor.create_order(
            instrument=instrument,
            direction=signal['direction'],
            units=units,
            stop_loss=signal['sl'],
            take_profit=signal['tps'][0] if signal['tps'] else None
        )
        
        if result['success']:
            self.log(f"✅ Trade executed!")
            return True
        else:
            self.log(f"❌ Failed: {result.get('error', 'Unknown')}")
            return False
    
    async def handle_message(self, event):
        try:
            text = event.message.text or ''
            if not text:
                return
            
            # Log
            entry = {'time': datetime.utcnow().isoformat(), 'text': text}
            with open(LOG_DIR / 'messages.jsonl', 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            self.log(f"💬 {text[:50]}...")
            
            # Parse
            signal = self.parse_signal(text)
            if signal:
                self.log(f"🚨 SIGNAL: {signal['symbol']} {signal['direction']}")
                self.save_signal(signal)
                
                # Auto-execute if complete
                if signal['sl'] and signal['tps']:
                    await self.execute_trade(signal)
                else:
                    self.log("   ⚠️ Incomplete signal")
                    
        except Exception as e:
            self.log(f"Error: {e}")
    
    async def run(self):
        self.log("=" * 50)
        self.log("Quanta Simple - Starting")
        self.log("=" * 50)
        
        # Write PID
        PID_FILE.write_text(str(os.getpid()))
        
        # Create client
        self.client = TelegramClient(str(SESSION_FILE), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                self.log("❌ Not authorized! Run: python3 auth.py")
                return 1
            
            me = await self.client.get_me()
            self.log(f"✓ Connected: {me.first_name}")
            
            # Find channel
            channel = None
            async for d in self.client.iter_dialogs():
                if CALLISTOFX_CHANNEL in d.name:
                    channel = d.id
                    self.log(f"✓ Channel: {d.name}")
                    break
            
            # Handler
            @self.client.on(events.NewMessage(chats=channel) if channel else events.NewMessage)
            async def handler(event):
                await self.handle_message(event)
            
            self.log("✓ Monitoring 24/7...")
            
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.log(f"Fatal: {e}")
            return 1
        finally:
            await self.client.disconnect()
            if PID_FILE.exists():
                PID_FILE.unlink()
        
        return 0

if __name__ == '__main__':
    q = SimpleQuanta()
    try:
        exit(asyncio.run(q.run()))
    except KeyboardInterrupt:
        print("\nStopped")