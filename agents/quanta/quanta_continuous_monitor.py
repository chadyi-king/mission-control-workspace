#!/usr/bin/env python3
"""
Quanta Continuous Monitor v4.0
Integrated with Helios Alert System
Monitors CallistoFX Premium channel 24/7 and alerts on signals
"""

import asyncio
import json
import os
import re
from datetime import datetime
from telethon import TelegramClient, events

# Load configs
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
SIGNALS_DIR = f'{BASE_DIR}/signals/PENDING'
BROADCAST_DIR = '/home/chad-yi/.openclaw/workspace/agents/message-bus/broadcast'
LOG_DIR = f'{BASE_DIR}/logs'
ALERT_LOG = f'{LOG_DIR}/signal_alerts.log'

# Ensure directories exist
os.makedirs(SIGNALS_DIR, exist_ok=True)
os.makedirs(BROADCAST_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize client - use existing authenticated session
SESSION_FILE = '/home/chad-yi/.openclaw/workspace/agents/quanta/quanta_session'
client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(ALERT_LOG, 'a') as f:
        f.write(log_entry + '\n')

def parse_trading_signal(text):
    """Parse CallistoFX signal format"""
    if not text:
        return None
    
    signal = {
        'id': f"SIG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'raw_text': text,
        'parsed_at': datetime.now().isoformat(),
        'source': 'CallistoFX Premium'
    }
    
    text_upper = text.upper()
    
    # Direction: BUY or SELL
    if 'BUY' in text_upper:
        signal['direction'] = 'BUY'
    elif 'SELL' in text_upper:
        signal['direction'] = 'SELL'
    else:
        return None
    
    # Symbol
    symbols = ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100', 'BTCUSD', 'ETHUSD', 'SPX500']
    for sym in symbols:
        if sym in text_upper:
            signal['pair'] = sym
            break
    
    if 'pair' not in signal:
        usd_match = re.search(r'(\w+)USD', text_upper)
        if usd_match:
            signal['pair'] = usd_match.group(0)
        else:
            return None
    
    # Entry range
    range_match = re.search(r'RANGE[:\s]+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text_upper)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        signal['entry'] = f"{low}-{high}"
        signal['entry_low'] = low
        signal['entry_high'] = high
    else:
        price_match = re.search(r'(?:ENTRY|@|AT)\s*[:\s]+(\d+\.?\d*)', text_upper)
        if price_match:
            price = float(price_match.group(1))
            signal['entry'] = str(price)
            signal['entry_low'] = price
            signal['entry_high'] = price
        else:
            # Try to find any two prices that could be range
            prices = re.findall(r'\d+\.?\d*', text)
            if len(prices) >= 2:
                nums = [float(p) for p in prices[:2]]
                signal['entry'] = f"{min(nums)}-{max(nums)}"
                signal['entry_low'] = min(nums)
                signal['entry_high'] = max(nums)
            else:
                return None
    
    # Stop Loss
    sl_match = re.search(r'SL[\s:]+(\d+\.?\d*)', text_upper)
    if sl_match:
        signal['sl'] = float(sl_match.group(1))
    else:
        return None
    
    # Take Profits
    tp_match = re.search(r'TP[\s:]+([\d./\s]+)', text_upper)
    if tp_match:
        tp_text = tp_match.group(1)
        tps = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
        signal['tps'] = tps
    else:
        # Try to find TP numbers after TP
        tps = re.findall(r'TP\d*[\s:]*(\d+\.?\d*)', text_upper)
        if tps:
            signal['tps'] = [float(tp) for tp in tps]
        else:
            return None
    
    return signal

def save_signal(signal):
    """Save signal to PENDING directory"""
    filepath = os.path.join(SIGNALS_DIR, f"{signal['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(signal, f, indent=2)
    return filepath

def alert_helios(signal):
    """Alert Helios via message-bus broadcast"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    alert_file = os.path.join(BROADCAST_DIR, f"urgent-quanta-{timestamp}.md")
    
    tps_str = '/'.join([str(tp) for tp in signal['tps']])
    
    alert_content = f"""🚨 TRADING SIGNAL ALERT

Source: {signal['source']}
Signal ID: {signal['id']}
Time: {signal['parsed_at']}

📊 SIGNAL DETAILS:
Pair: {signal['pair']}
Direction: {signal['direction']}
Entry: {signal['entry']}
SL: {signal['sl']}
TPs: {tps_str}

📁 Signal file: /agents/quanta/signals/PENDING/{signal['id']}.json

---
QUANTA Trading Agent | Auto-generated alert
"""
    
    with open(alert_file, 'w') as f:
        f.write(alert_content)
    
    return alert_file

async def find_callistofx_channel():
    """Find the CallistoFx channel"""
    log("🔍 Searching for CallistoFx Premium channel...")
    
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if "callistofx" in name.lower() and "premium" in name.lower():
            log(f"✅ Found: {name} (ID: {dialog.id})")
            return dialog.id
    
    log("❌ Channel not found")
    return None

async def main():
    """Main entry point"""
    log("=" * 60)
    log("🚀 Quanta Continuous Monitor v4.0")
    log("   Integrated with Helios Alert System")
    log("=" * 60)
    
    # Connect to Telegram
    await client.start(phone=lambda: PHONE_NUMBER)
    me = await client.get_me()
    log(f"✅ Logged in as: {me.first_name}")
    
    # Find channel
    channel_id = await find_callistofx_channel()
    if not channel_id:
        log("❌ Could not find CallistoFX Premium channel")
        return
    
    log(f"🎯 MONITORING ACTIVE - Waiting for signals...")
    log(f"📁 Signals: {SIGNALS_DIR}")
    log(f"📢 Alerts: {BROADCAST_DIR}")
    log("-" * 60)
    
    # Message handler
    @client.on(events.NewMessage(chats=channel_id))
    async def handle_message(event):
        text = event.message.text
        if not text:
            return
        
        # Check if it's a signal
        signal = parse_trading_signal(text)
        
        if signal:
            log(f"🚨 SIGNAL DETECTED: {signal['pair']} {signal['direction']}")
            log(f"   Entry: {signal['entry']} | SL: {signal['sl']} | TPs: {signal['tps']}")
            
            # Save signal
            signal_file = save_signal(signal)
            log(f"   ✅ Saved: {signal_file}")
            
            # Alert Helios
            alert_file = alert_helios(signal)
            log(f"   🚨 HELIOS ALERTED: {alert_file}")
            
            log("-" * 60)
        else:
            # Log non-signal messages for reference
            preview = text[:60].replace('\n', ' ')
            log(f"💬 Message: {preview}...")
    
    # Run forever
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
