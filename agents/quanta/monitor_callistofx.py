#!/usr/bin/env python3
"""
Quanta CALLISTOFX Monitor
Reads your personal Telegram and monitors CALLISTOFX channel for trading signals
"""

from telethon import TelegramClient, events
import json
import re
from datetime import datetime
import os

# Load config
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, CALLISTOFX_CHANNEL

# Session file (keeps you logged in)
SESSION_FILE = '/agents/quanta/quanta_telegram_session'

# Initialize client
client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)

print(f"[{datetime.now()}] Quanta: Initializing Telegram monitor...")
print(f"[{datetime.now()}] Quanta: Will monitor {CALLISTOFX_CHANNEL} channel")

@client.on(events.NewMessage(chats=CALLISTOFX_CHANNEL))
async def handle_new_message(event):
    """Process new messages from CALLISTOFX"""
    message = event.message.text
    timestamp = datetime.now()
    
    print(f"\n[{timestamp}] 📨 New message from CALLISTOFX:")
    print(f"Content: {message[:200]}...")
    
    # Parse trading signal
    signal = parse_trading_signal(message)
    
    if signal:
        print(f"✅ SIGNAL DETECTED: {signal}")
        
        # Save to inbox
        signal_data = {
            'timestamp': timestamp.isoformat(),
            'source': 'CALLISTOFX',
            'raw_message': message,
            'parsed_signal': signal
        }
        
        # Append to signals log
        with open('/agents/quanta/inbox/callistofx_signals.jsonl', 'a') as f:
            f.write(json.dumps(signal_data) + '\n')
        
        # Alert CHAD_YI
        alert = {
            'type': 'trading_signal',
            'agent': 'quanta',
            'timestamp': timestamp.isoformat(),
            'signal': signal,
            'action_required': 'review_and_execute'
        }
        
        with open('/agents/quanta/outbox/signal_alert.json', 'w') as f:
            json.dump(alert, f, indent=2)
        
        print(f"📁 Signal saved to inbox")
        print(f"📤 Alert sent to CHAD_YI")
        
    else:
        print(f"ℹ️ Not a trading signal (general message)")

def parse_trading_signal(text):
    """
    Parse CALLISTOFX trading signal format
    Examples:
    - "BUY EURUSD @ 1.0850 | SL: 1.0820 | TP: 1.0900"
    - "SELL XAUUSD @ 2030.50 | SL: 2040.00 | TP: 2010.00"
    """
    signal = {}
    text_upper = text.upper()
    
    # Action: BUY or SELL
    if 'BUY' in text_upper:
        signal['action'] = 'BUY'
    elif 'SELL' in text_upper:
        signal['action'] = 'SELL'
    else:
        return None
    
    # Currency pair (XAUUSD, EURUSD, GBPUSD, etc.)
    pair_patterns = [
        r'(XAU|XAG)(USD)',
        r'(EUR|GBP|USD|AUD|CAD|CHF|JPY|NZD)(USD|EUR|GBP|JPY|AUD|CAD|CHF)'
    ]
    
    for pattern in pair_patterns:
        match = re.search(pattern, text_upper)
        if match:
            signal['pair'] = match.group(0)
            break
    
    if 'pair' not in signal:
        return None
    
    # Entry price
    entry_match = re.search(r'@\s*(\d+\.?\d*)', text)
    if entry_match:
        signal['entry'] = float(entry_match.group(1))
    
    # Stop Loss
    sl_match = re.search(r'SL[:\s]+(\d+\.?\d*)', text_upper)
    if sl_match:
        signal['stop_loss'] = float(sl_match.group(1))
    
    # Take Profit
    tp_match = re.search(r'TP[:\s]+(\d+\.?\d*)', text_upper)
    if tp_match:
        signal['take_profit'] = float(tp_match.group(1))
    
    # Only return if we have minimum required fields
    if len(signal) >= 4:
        return signal
    
    return None

async def main():
    """Main entry point"""
    print(f"[{datetime.now()}] 🔐 Connecting to Telegram...")
    
    # Start the client (will ask for code on first run)
    await client.start(phone=PHONE_NUMBER)
    
    me = await client.get_me()
    print(f"[{datetime.now()}] ✅ Logged in as: {me.first_name} (@{me.username})")
    
    # Get CALLISTOFX channel info
    try:
        channel = await client.get_entity(CALLISTOFX_CHANNEL)
        print(f"[{datetime.now()}] 📡 Monitoring channel: {channel.title}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error finding channel: {e}")
        print(f"[{datetime.now()}] Make sure you're subscribed to {CALLISTOFX_CHANNEL}")
        return
    
    print(f"\n[{datetime.now()}] 🚀 Quanta is now monitoring CALLISTOFX...")
    print(f"[{datetime.now()}] Press Ctrl+C to stop\n")
    
    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    import sys
    
    # Check if config is filled
    if "YOUR_API_ID_HERE" in TELEGRAM_API_ID:
        print("❌ ERROR: Please fill in your actual API credentials in telegram_config.py")
        print("   Get them from: https://my.telegram.org/apps")
        sys.exit(1)
    
    if "YOUR_NUMBER" in PHONE_NUMBER:
        print("❌ ERROR: Please fill in your phone number in telegram_config.py")
        sys.exit(1)
    
    # Run the monitor
    with client:
        client.loop.run_until_complete(main())
