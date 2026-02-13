#!/usr/bin/env python3
"""
Quanta Signal Watcher v2.0
Watches the existing monitor's message log and triggers alerts on FRESH signals only
CRITICAL: Only captures signals from LAST 5 MINUTES
"""

import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
SIGNALS_DIR = f'{BASE_DIR}/signals/PENDING'
BROADCAST_DIR = '/home/chad-yi/.openclaw/workspace/agents/message-bus/broadcast'
LOG_DIR = f'{BASE_DIR}/logs'
MESSAGES_FILE = f'{LOG_DIR}/all_messages.jsonl'
WATCHER_LOG = f'{LOG_DIR}/watcher.log'

# CRITICAL: Only capture signals from last 5 minutes
MAX_AGE_SECONDS = 300  # 5 minutes

# Invalidating keywords
INVALIDATING_KEYWORDS = ['closed', 'cancelled', 'expired', 'stopped out', 'hit sl', 'done', 'finished', 'position closed']

# Ensure directories exist
os.makedirs(SIGNALS_DIR, exist_ok=True)
os.makedirs(BROADCAST_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(WATCHER_LOG, 'a') as f:
        f.write(log_entry + '\n')

def parse_timestamp(ts_str):
    """Parse ISO timestamp string to datetime"""
    try:
        # Handle various ISO formats
        ts_str = ts_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts_str)
    except:
        return None

def is_fresh_message(msg_timestamp_str):
    """
    CRITICAL: Check if message is from last 5 minutes
    Returns True if message is fresh (< 5 min old)
    """
    msg_time = parse_timestamp(msg_timestamp_str)
    if not msg_time:
        return False
    
    # Convert to UTC for comparison
    now = datetime.now(timezone.utc)
    if msg_time.tzinfo is None:
        msg_time = msg_time.replace(tzinfo=timezone.utc)
    
    age_seconds = (now - msg_time).total_seconds()
    
    if age_seconds >= MAX_AGE_SECONDS:
        # Don't log every old message - only log if debugging
        # log(f"SKIP: Message too old ({int(age_seconds)}s >= {MAX_AGE_SECONDS}s)")
        return False
    
    return True

def is_invalidated_by_context(signal_text, recent_messages):
    """
    Check if signal is invalidated by recent context
    Looks for 'closed', 'expired', etc. in recent messages
    """
    text_upper = signal_text.upper()
    
    # Extract pair from signal
    pair = None
    symbols = ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100', 'BTCUSD', 'ETHUSD', 'SPX500']
    for sym in symbols:
        if sym in text_upper:
            pair = sym
            break
    
    if not pair:
        return False, "No pair found"
    
    # Check recent messages for invalidating context
    for msg in recent_messages:
        msg_text = msg.get('text', '').lower()
        if pair.lower() in msg_text:
            for keyword in INVALIDATING_KEYWORDS:
                if keyword in msg_text:
                    return True, f"Signal invalidated: '{keyword}' found in recent context"
    
    return False, "Context clean"

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
        signal['entry_mid'] = (low + high) / 2
    else:
        # Try to find prices
        prices = re.findall(r'\d+\.?\d*', text)
        if len(prices) >= 2:
            nums = sorted([float(p) for p in prices[:4] if float(p) > 1000])
            if len(nums) >= 2:
                signal['entry'] = f"{nums[0]}-{nums[1]}"
                signal['entry_low'] = nums[0]
                signal['entry_high'] = nums[1]
                signal['entry_mid'] = (nums[0] + nums[1]) / 2
            elif len(nums) == 1:
                signal['entry'] = str(nums[0])
                signal['entry_low'] = nums[0]
                signal['entry_high'] = nums[0]
                signal['entry_mid'] = nums[0]
            else:
                return None
        else:
            return None
    
    # Stop Loss - look for SL followed by number
    sl_match = re.search(r'SL[\s:]+(\d+\.?\d*)', text_upper)
    if sl_match:
        signal['sl'] = float(sl_match.group(1))
    else:
        # Try alternate patterns
        sl_alt = re.search(r'STOP\s*LOSS[\s:]+(\d+\.?\d*)', text_upper)
        if sl_alt:
            signal['sl'] = float(sl_alt.group(1))
        else:
            return None
    
    # Take Profits
    tp_match = re.search(r'TP[\s:]+([\d./\s,]+)', text_upper)
    if tp_match:
        tp_text = tp_match.group(1)
        tps = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
        if tps:
            signal['tps'] = tps
        else:
            return None
    else:
        # Try TP1, TP2, etc pattern
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

def alert_helios(signal, age_seconds):
    """Alert Helios via message-bus broadcast"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    alert_file = os.path.join(BROADCAST_DIR, f"urgent-quanta-{timestamp}.md")
    
    tps_str = '/'.join([str(tp) for tp in signal['tps']])
    
    alert_content = f"""🚨 FRESH SIGNAL CAPTURED ({int(age_seconds)}s old)

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
QUANTA Trading Agent | Fresh Signal Alert
"""
    
    with open(alert_file, 'w') as f:
        f.write(alert_content)
    
    return alert_file

def load_recent_messages(limit=10):
    """Load recent messages for context checking"""
    messages = []
    if not os.path.exists(MESSAGES_FILE):
        return messages
    
    with open(MESSAGES_FILE, 'r') as f:
        lines = f.readlines()
        for line in lines[-limit:]:
            try:
                msg = json.loads(line.strip())
                messages.append(msg)
            except:
                continue
    
    return messages

def process_new_messages():
    """
    Process new messages from log file
    CRITICAL: Only processes messages from last 5 minutes
    """
    if not os.path.exists(MESSAGES_FILE):
        log(f"⚠️  Messages file not found: {MESSAGES_FILE}")
        return 0
    
    processed = 0
    signals_found = 0
    
    # Load recent messages for context checking
    recent_messages = load_recent_messages(10)
    
    with open(MESSAGES_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                msg = json.loads(line)
                text = msg.get('text', '')
                timestamp_str = msg.get('timestamp', '')
                
                # CRITICAL: Skip if message is older than 5 minutes
                if not is_fresh_message(timestamp_str):
                    continue
                
                # Check if it's a signal
                signal = parse_trading_signal(text)
                
                if signal:
                    signals_found += 1
                    
                    # Check for invalidating context
                    is_invalid, reason = is_invalidated_by_context(text, recent_messages)
                    if is_invalid:
                        log(f"SKIP: {reason}")
                        continue
                    
                    # Calculate age for alert
                    msg_time = parse_timestamp(timestamp_str)
                    now = datetime.now(timezone.utc)
                    if msg_time.tzinfo is None:
                        msg_time = msg_time.replace(tzinfo=timezone.utc)
                    age_seconds = (now - msg_time).total_seconds()
                    
                    log(f"🚨 FRESH SIGNAL DETECTED: {signal['pair']} {signal['direction']} ({int(age_seconds)}s old)")
                    
                    # Save signal
                    signal_file = save_signal(signal)
                    log(f"   ✅ Saved: {signal_file}")
                    
                    # Alert Helios
                    alert_file = alert_helios(signal, age_seconds)
                    log(f"   🚨 HELIOS ALERTED: {alert_file}")
                    
                    processed += 1
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                log(f"❌ Error processing message: {e}")
                continue
    
    return processed

def watch_continuously():
    """Watch for new signals continuously"""
    log("=" * 60)
    log("🔭 Quanta Signal Watcher v2.0 - FRESH SIGNALS ONLY")
    log(f"   Max age: {MAX_AGE_SECONDS}s (5 minutes)")
    log("   Watching: " + MESSAGES_FILE)
    log("=" * 60)
    
    # Get initial file size
    last_size = os.path.getsize(MESSAGES_FILE) if os.path.exists(MESSAGES_FILE) else 0
    
    while True:
        try:
            if os.path.exists(MESSAGES_FILE):
                current_size = os.path.getsize(MESSAGES_FILE)
                
                if current_size > last_size:
                    log(f"📨 New messages detected ({current_size - last_size} bytes)")
                    count = process_new_messages()
                    if count > 0:
                        log(f"✅ {count} fresh signal(s) captured")
                    last_size = current_size
            else:
                log(f"⚠️  Messages file not found, waiting...")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            log("\n👋 Watcher stopped by user")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    watch_continuously()
