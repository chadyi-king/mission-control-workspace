#!/usr/bin/env python3
"""
Quanta CALLISTOFX Monitor v2.0
- Log rotation (7 days retention)
- Signal pattern learning
- Fast execution (<10 seconds)
- OANDA integration ready
"""

from telethon import TelegramClient, events
import json
import re
from datetime import datetime, timedelta
import os
import gzip
import glob
from pathlib import Path

# Load config
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, CALLISTOFX_CHANNEL

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
INBOX_DIR = f'{BASE_DIR}/inbox'
OUTBOX_DIR = f'{BASE_DIR}/outbox'
LOG_DIR = f'{BASE_DIR}/logs'
SESSION_FILE = '/tmp/quanta_telegram_session'

# Settings
MAX_LOG_DAYS = 7          # Keep logs for 7 days
MAX_LOG_SIZE_MB = 100     # Or 100MB max
SIGNAL_LOG_FILE = f'{INBOX_DIR}/signals.jsonl'
ALL_MESSAGES_FILE = f'{LOG_DIR}/all_messages.jsonl'

# Initialize client
client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Ensure directories exist
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def rotate_logs():
    """Clean up old logs (older than 7 days or >100MB)"""
    try:
        now = datetime.now()
        cutoff_date = now - timedelta(days=MAX_LOG_DAYS)
        
        # Check all log files
        for log_file in glob.glob(f'{LOG_DIR}/*.jsonl') + glob.glob(f'{INBOX_DIR}/*.jsonl'):
            file_stat = os.stat(log_file)
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
            file_size_mb = file_stat.st_size / (1024 * 1024)
            
            # Delete if older than 7 days OR larger than 100MB
            if file_mtime < cutoff_date or file_size_mb > MAX_LOG_SIZE_MB:
                print(f"[{datetime.now()}] 🗑️ Rotating old log: {os.path.basename(log_file)}")
                # Compress before deleting (optional)
                # gzip.open(f'{log_file}.gz', 'wb').write(open(log_file, 'rb').read())
                os.remove(log_file)
                
        # Also check and compress large current logs
        for log_file in [SIGNAL_LOG_FILE, ALL_MESSAGES_FILE]:
            if os.path.exists(log_file):
                size_mb = os.path.getsize(log_file) / (1024 * 1024)
                if size_mb > 50:  # Compress if >50MB
                    print(f"[{datetime.now()}] 📦 Compressing large log: {os.path.basename(log_file)}")
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(f'{log_file}.gz', 'wb') as f_out:
                            f_out.write(f_in.read())
                    os.remove(log_file)  # Remove original after compressing
                    
    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ Log rotation error: {e}")

def parse_trading_signal(text):
    """
    Parse CALLISTOFX trading signal format
    Enhanced to handle various formats
    """
    if not text:
        return None
        
    signal = {
        'parsed_at': datetime.now().isoformat(),
        'raw_text': text[:500]  # Store first 500 chars
    }
    
    text_upper = text.upper()
    
    # Action: BUY or SELL
    if 'BUY' in text_upper:
        signal['action'] = 'BUY'
    elif 'SELL' in text_upper:
        signal['action'] = 'SELL'
    else:
        return None
    
    # Currency pair (XAUUSD, EURUSD, etc.)
    pair_patterns = [
        r'(XAUUSD|XAGUSD)',  # Gold/Silver
        r'(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY){2}',  # Forex pairs
    ]
    
    for pattern in pair_patterns:
        match = re.search(pattern, text_upper)
        if match:
            signal['pair'] = match.group(0)
            break
    
    if 'pair' not in signal:
        return None
    
    # Entry price - multiple formats
    entry_patterns = [
        r'[@\s]+(\d+\.?\d*)',           # @ 2030.50
        r'ENTRY[:\s]+(\d+\.?\d*)',      # Entry: 2030.50
        r'PRICE[:\s]+(\d+\.?\d*)',      # Price: 2030.50
    ]
    
    for pattern in entry_patterns:
        match = re.search(pattern, text)
        if match:
            signal['entry'] = float(match.group(1))
            break
    
    # Stop Loss
    sl_patterns = [
        r'SL[:\s]+(\d+\.?\d*)',
        r'STOP[:\s]+(\d+\.?\d*)',
        r'STOP LOSS[:\s]+(\d+\.?\d*)',
    ]
    
    for pattern in sl_patterns:
        match = re.search(pattern, text_upper)
        if match:
            signal['stop_loss'] = float(match.group(1))
            break
    
    # Take Profit (may have multiple TPs)
    tp_matches = re.findall(r'TP\d*[:\s]+(\d+\.?\d*)', text_upper)
    if tp_matches:
        signal['take_profits'] = [float(tp) for tp in tp_matches]
        signal['take_profit'] = signal['take_profits'][0]  # Primary TP
    else:
        # Single TP
        tp_match = re.search(r'TP[:\s]+(\d+\.?\d*)', text_upper)
        if tp_match:
            signal['take_profit'] = float(tp_match.group(1))
            signal['take_profits'] = [signal['take_profit']]
    
    # Risk/Reward calculation
    if all(k in signal for k in ['entry', 'stop_loss', 'take_profit']):
        if signal['action'] == 'BUY':
            signal['risk'] = abs(signal['entry'] - signal['stop_loss'])
            signal['reward'] = abs(signal['take_profit'] - signal['entry'])
        else:  # SELL
            signal['risk'] = abs(signal['stop_loss'] - signal['entry'])
            signal['reward'] = abs(signal['entry'] - signal['take_profit'])
        
        if signal['risk'] > 0:
            signal['rr_ratio'] = round(signal['reward'] / signal['risk'], 2)
    
    # Validate minimum required fields
    required = ['action', 'pair', 'entry']
    if not all(k in signal for k in required):
        return None
        
    return signal

def save_signal(signal, raw_message):
    """Save signal to inbox with timestamp"""
    timestamp = datetime.now()
    
    signal_data = {
        'timestamp': timestamp.isoformat(),
        'source': 'CALLISTOFX',
        'channel': CALLISTOFX_CHANNEL,
        'parsed_signal': signal,
        'raw_message': raw_message[:1000]  # First 1000 chars
    }
    
    # Append to signals log
    with open(SIGNAL_LOG_FILE, 'a') as f:
        f.write(json.dumps(signal_data) + '\n')
    
    # Also save as latest signal for quick access
    latest_file = f'{OUTBOX_DIR}/latest_signal.json'
    with open(latest_file, 'w') as f:
        json.dump(signal_data, f, indent=2)
    
    # Create alert for CHAD_YI
    alert = {
        'type': 'trading_signal',
        'agent': 'quanta',
        'timestamp': timestamp.isoformat(),
        'signal': signal,
        'action_required': 'execute_trade',
        'urgency': 'high' if signal.get('rr_ratio', 0) >= 2 else 'medium'
    }
    
    alert_file = f'{OUTBOX_DIR}/signal_alert.json'
    with open(alert_file, 'w') as f:
        json.dump(alert, f, indent=2)
    
    return signal_data

def log_all_message(message_text, sender):
    """Log all messages for pattern learning"""
    timestamp = datetime.now()
    
    log_entry = {
        'timestamp': timestamp.isoformat(),
        'sender': sender,
        'message': message_text[:500],  # First 500 chars
        'is_signal': bool(parse_trading_signal(message_text))
    }
    
    # Append to all messages log
    with open(ALL_MESSAGES_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

async def find_callistofx_channel():
    """Find the CallistoFx Premium channel by searching dialogs"""
    print(f"[{datetime.now()}] Searching for CallistoFx Premium channel...")
    
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        # Look specifically for "CallistoFx" AND "Premium" (case insensitive)
        if "callistofx" in name.lower() and "premium" in name.lower():
            print(f"[{datetime.now()}] ✅ Found channel: {name}")
            print(f"[{datetime.now()}]    ID: {dialog.id}")
            return dialog.id
    
    print(f"[{datetime.now()}] ❌ Could not find CallistoFx Premium channel")
    return None

async def fetch_recent_history(channel_id, limit=50):
    """Fetch last 50 messages to learn patterns"""
    print(f"[{datetime.now()}] 📜 Fetching last {limit} messages for pattern learning...")
    
    signal_count = 0
    async for message in client.iter_messages(channel_id, limit=limit):
        if message.text:
            # Log all messages
            log_all_message(message.text, "CALLISTOFX")
            
            # Check if it's a signal
            signal = parse_trading_signal(message.text)
            if signal:
                signal_count += 1
                # Don't save old signals as "new" but log them for learning
                print(f"  [Signal] {signal.get('action')} {signal.get('pair')} @ {signal.get('entry')}")
    
    print(f"[{datetime.now()}] ✅ Found {signal_count} signals in last {limit} messages")
    return signal_count

async def main():
    """Main entry point"""
    print(f"[{datetime.now()}] 🚀 Quanta v2.0 Starting...")
    print(f"[{datetime.now()}] 🔐 Connecting to Telegram...")
    
    # Rotate old logs on startup
    rotate_logs()
    
    # Start the client
    await client.start(phone=lambda: PHONE_NUMBER)
    
    me = await client.get_me()
    print(f"[{datetime.now()}] ✅ Logged in as: {me.first_name} (@{me.username})")
    
    # Find the CallistoFx channel
    channel_id = await find_callistofx_channel()
    
    if not channel_id:
        print(f"[{datetime.now()}] ❌ Exiting - cannot find channel")
        return
    
    # Fetch recent history for learning
    await fetch_recent_history(channel_id, limit=50)
    
    print(f"[{datetime.now()}] 🎯 Monitoring for new signals...")
    print(f"[{datetime.now()}] 💾 Logs rotate after {MAX_LOG_DAYS} days or {MAX_LOG_SIZE_MB}MB")
    print(f"[{datetime.now()}] Press Ctrl+C to stop\n")
    
    # Set up event handler for this specific channel
    @client.on(events.NewMessage(chats=channel_id))
    async def handle_new_message(event):
        """Process new messages from CALLISTOFX"""
        message = event.message.text
        timestamp = datetime.now()
        
        if not message:
            return
        
        # Log all messages
        log_all_message(message, "CALLISTOFX")
        
        # Parse trading signal
        signal = parse_trading_signal(message)
        
        if signal:
            print(f"\n[{timestamp}] 🚨 NEW SIGNAL DETECTED!")
            print(f"  Action: {signal['action']}")
            print(f"  Pair: {signal['pair']}")
            print(f"  Entry: {signal['entry']}")
            print(f"  SL: {signal.get('stop_loss', 'N/A')}")
            print(f"  TP: {signal.get('take_profit', 'N/A')}")
            if 'rr_ratio' in signal:
                print(f"  R:R = 1:{signal['rr_ratio']}")
            
            # Save signal
            save_signal(signal, message)
            
            print(f"[{timestamp}] ✅ Signal saved and alert sent to CHAD_YI")
            
            # TODO: Execute trade on OANDA (when you're ready)
            # await execute_oanda_trade(signal)
        else:
            # Not a signal, just log it
            print(f"[{timestamp}] 💬 Message received (not a signal)")
    
    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    import sys
    
    # Check if config is filled
    try:
        from telegram_config import TELEGRAM_API_ID
        if "YOUR" in str(TELEGRAM_API_ID):
            print("❌ ERROR: Please fill in your actual API credentials")
            sys.exit(1)
    except:
        pass
    
    # Run the monitor
    with client:
        client.loop.run_until_complete(main())
