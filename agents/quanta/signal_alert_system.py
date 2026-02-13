#!/usr/bin/env python3
"""
Quanta Signal Alert System
Monitors for new trading signals and alerts Helios immediately via message-bus
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
INBOX_DIR = f'{BASE_DIR}/inbox'
SIGNALS_DIR = f'{BASE_DIR}/signals/PENDING'
BROADCAST_DIR = '/home/chad-yi/.openclaw/workspace/agents/message-bus/broadcast'
LOG_FILE = f'{BASE_DIR}/logs/signal_alerts.log'

# Ensure directories exist
os.makedirs(SIGNALS_DIR, exist_ok=True)
os.makedirs(BROADCAST_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + '\n')

def parse_trading_signal(text):
    """
    Parse CallistoFX signal format:
    🟢XAUUSD🟢
    BUY
    RANGE: 2680-2685
    SL 2675
    TP : 2700/2720/2740/2760/2780
    """
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
    
    # Symbol (pair)
    symbols = ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100', 'BTCUSD', 'ETHUSD']
    for sym in symbols:
        if sym in text_upper:
            signal['pair'] = sym
            break
    
    if 'pair' not in signal:
        # Try to extract any word before USD
        usd_match = re.search(r'(\w+)USD', text_upper)
        if usd_match:
            signal['pair'] = usd_match.group(0)
        else:
            return None
    
    # Entry range: "RANGE: 2680-2685" or "2680 - 2685"
    range_match = re.search(r'RANGE[:\s]+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text_upper)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        signal['entry'] = f"{low}-{high}"
        signal['entry_low'] = low
        signal['entry_high'] = high
    else:
        # Single price entry
        price_match = re.search(r'(?:ENTRY|@|AT)\s*[:\s]+(\d+\.?\d*)', text_upper)
        if price_match:
            price = float(price_match.group(1))
            signal['entry'] = str(price)
            signal['entry_low'] = price
            signal['entry_high'] = price
        else:
            return None
    
    # Stop Loss
    sl_match = re.search(r'SL[\s:]+(\d+\.?\d*)', text_upper)
    if sl_match:
        signal['sl'] = float(sl_match.group(1))
    else:
        return None
    
    # Take Profits (can be multiple)
    tp_match = re.search(r'TP[\s:]+([\d./\s]+)', text_upper)
    if tp_match:
        tp_text = tp_match.group(1)
        # Extract all numbers separated by / or space
        tps = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
        signal['tps'] = tps
    else:
        return None
    
    return signal

def save_signal(signal):
    """Save signal to PENDING directory"""
    filepath = os.path.join(SIGNALS_DIR, f"{signal['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(signal, f, indent=2)
    log(f"✅ Signal saved: {filepath}")
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
    
    log(f"🚨 HELIOS ALERT SENT: {alert_file}")
    return alert_file

def process_message(text):
    """Process a message and alert if it's a signal"""
    log(f"Checking message: {text[:80]}...")
    
    signal = parse_trading_signal(text)
    
    if signal:
        log(f"🎯 SIGNAL DETECTED: {signal['pair']} {signal['direction']}")
        
        # Save to PENDING
        save_signal(signal)
        
        # Alert Helios
        alert_file = alert_helios(signal)
        
        log(f"✅ Signal captured and Helios alerted!")
        return signal, alert_file
    else:
        log("ℹ️  Not a trading signal")
        return None, None

if __name__ == '__main__':
    log("🚀 Quanta Signal Alert System initialized")
    log(f"📁 Signals dir: {SIGNALS_DIR}")
    log(f"📢 Broadcast dir: {BROADCAST_DIR}")
    
    # Test with sample signal
    test_signal = """🟢XAUUSD🟢
BUY
RANGE: 2680-2685
SL 2675
TP : 2700/2720/2740/2760/2780"""
    
    log("\n🧪 Testing with sample signal...")
    signal, alert = process_message(test_signal)
    
    if signal:
        log(f"\n✅ TEST PASSED - Signal parsing works!")
        log(f"   Pair: {signal['pair']}")
        log(f"   Direction: {signal['direction']}")
        log(f"   Entry: {signal['entry']}")
        log(f"   SL: {signal['sl']}")
        log(f"   TPs: {signal['tps']}")
