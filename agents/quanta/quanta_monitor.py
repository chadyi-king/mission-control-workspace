#!/usr/bin/env python3
"""
Quanta - Simple 24/7 Monitor
One file. No complexity. Just works.
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

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
INBOX_DIR = BASE_DIR / 'inbox'
SESSION_FILE = BASE_DIR / 'sessions' / 'quanta'
PID_FILE = BASE_DIR / 'quanta.pid'

LOG_DIR.mkdir(exist_ok=True)
INBOX_DIR.mkdir(exist_ok=True)
(SESSION_FILE.parent).mkdir(exist_ok=True)

sys.path.insert(0, str(BASE_DIR))
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, CALLISTOFX_CHANNEL

running = True

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_DIR / 'quanta.log', 'a') as f:
        f.write(line + '\n')

def save_msg(text):
    entry = {'time': datetime.utcnow().isoformat(), 'text': text}
    with open(LOG_DIR / 'messages.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

def parse_signal(text):
    up = text.upper()
    if 'BUY' not in up and 'SELL' not in up:
        return None
    
    symbols = ['XAUUSD', 'XAGUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY',
               'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY',
               'AUDJPY', 'CADJPY', 'CHFJPY', 'NZDJPY', 'EURAUD', 'EURCHF', 'GBPAUD',
               'GBPCAD', 'GBPCHF', 'US30', 'NAS100']
    sym = next((s for s in symbols if s in up), None)
    if not sym:
        return None
    
    return {
        'symbol': sym,
        'direction': 'BUY' if 'BUY' in up else 'SELL',
        'text': text[:100]
    }

async def main():
    global running
    
    log("=" * 40)
    log("Quanta Starting")
    log("=" * 40)
    
    # Write PID
    PID_FILE.write_text(str(os.getpid()))
    
    client = TelegramClient(str(SESSION_FILE), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            log("❌ Not authorized! Run: python3 auth.py")
            return 1
        
        me = await client.get_me()
        log(f"✓ Connected as: {me.first_name}")
        
        # Find channel
        channel = None
        async for d in client.iter_dialogs():
            if CALLISTOFX_CHANNEL in d.name:
                channel = d.id
                log(f"✓ Found channel: {d.name}")
                break
        
        @client.on(events.NewMessage(chats=channel) if channel else events.NewMessage)
        async def handler(event):
            try:
                text = event.message.text or ''
                if not text:
                    return
                
                save_msg(text)
                preview = text[:40].replace('\n', ' ')
                log(f"💬 {preview}...")
                
                sig = parse_signal(text)
                if sig:
                    log(f"🚨 SIGNAL: {sig['symbol']} {sig['direction']}")
                    with open(INBOX_DIR / f"sig_{datetime.now():%H%M%S}.json", 'w') as f:
                        json.dump(sig, f)
                        
            except Exception as e:
                log(f"Error: {e}")
        
        log("✓ Monitoring 24/7...")
        
        while running:
            await asyncio.sleep(1)
            
    except Exception as e:
        log(f"Fatal: {e}")
        return 1
    finally:
        await client.disconnect()
        if PID_FILE.exists():
            PID_FILE.unlink()
        log("Stopped")
    
    return 0

def shutdown(signum, frame):
    global running
    running = False
    log("Shutting down...")

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\nBye")
        sys.exit(0)