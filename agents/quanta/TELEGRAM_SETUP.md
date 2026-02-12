# Quanta Telegram Channel Monitor Setup

## Goal
Configure Quanta (A5 Trading Agent) to read your personal Telegram and monitor the **CALLISTOFX** channel for trading signals.

## What This Enables
- Quanta reads CALLISTOFX channel in real-time
- Extracts trading signals (entry, exit, SL, TP)
- Auto-executes or asks for approval
- Logs all activity

## Setup Steps

### Step 1: Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create new app:
   - App name: `QuantaTrader`
   - Short name: `quanta`
   - Platform: `Desktop`
   - Description: `Trading bot for CALLISTOFX signals`
4. Save the credentials:
   - **API ID**: (numbers)
   - **API Hash**: (long string)

### Step 2: Install Telethon

```bash
pip install telethon
```

### Step 3: Initial Authentication (One-time)

Create `/agents/quanta/telegram_auth.py`:

```python
from telethon import TelegramClient

# Your credentials
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone = 'YOUR_PHONE_NUMBER'  # +6591234567

client = TelegramClient('quanta_session', api_id, api_hash)

async def main():
    await client.start(phone)
    print("Authenticated successfully!")
    
    # List all channels you're in
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            print(f"{dialog.id}: {dialog.title}")
    
    # Find CALLISTOFX channel ID
    # Look for the channel in the list above

with client:
    client.loop.run_until_complete(main())
```

Run once:
```bash
cd /agents/quanta
python telegram_auth.py
```

You'll receive an SMS code. Enter it. This creates `quanta_session.session` file.

### Step 4: Monitor CALLISTOFX Channel

Create `/agents/quanta/callistofx_monitor.py`:

```python
from telethon import TelegramClient, events
import json
import re
from datetime import datetime

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'

# CALLISTOFX channel ID (from step 3)
CALLISTOFX_CHANNEL_ID = -1001234567890  # Replace with actual ID

client = TelegramClient('quanta_session', api_id, api_hash)

class TradingSignal:
    def __init__(self, pair, action, entry, sl, tp):
        self.pair = pair
        self.action = action  # BUY or SELL
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            'pair': self.pair,
            'action': self.action,
            'entry': self.entry,
            'sl': self.sl,
            'tp': self.tp,
            'timestamp': self.timestamp.isoformat()
        }

def parse_signal(text):
    """Parse CALLISTOFX signal format"""
    # Example: "BUY EURUSD @ 1.0850 | SL: 1.0820 | TP: 1.0900"
    
    signal = {}
    
    # Extract BUY/SELL
    if 'BUY' in text.upper():
        signal['action'] = 'BUY'
    elif 'SELL' in text.upper():
        signal['action'] = 'SELL'
    
    # Extract pair (EURUSD, GBPUSD, XAUUSD, etc.)
    pair_match = re.search(r'(EUR|GBP|USD|JPY|AUD|CAD|CHF|NZD|XAU|XAG)(USD|EUR|GBP|JPY|AUD|CAD|CHF)', text)
    if pair_match:
        signal['pair'] = pair_match.group(0)
    
    # Extract entry price
    entry_match = re.search(r'@\s*(\d+\.\d+)', text)
    if entry_match:
        signal['entry'] = float(entry_match.group(1))
    
    # Extract SL
    sl_match = re.search(r'SL[:\s]+(\d+\.\d+)', text)
    if sl_match:
        signal['sl'] = float(sl_match.group(1))
    
    # Extract TP
    tp_match = re.search(r'TP[:\s]+(\d+\.\d+)', text)
    if tp_match:
        signal['tp'] = float(tp_match.group(1))
    
    return signal if len(signal) >= 4 else None

@client.on(events.NewMessage(chats=CALLISTOFX_CHANNEL_ID))
async def handler(event):
    message = event.message.text
    
    print(f"[CALLISTOFX] {datetime.now()}: {message[:100]}...")
    
    # Parse signal
    signal = parse_signal(message)
    
    if signal:
        print(f"✅ Signal detected: {signal}")
        
        # Save to file for Quanta to process
        signal['received_at'] = datetime.now().isoformat()
        
        with open('/agents/quanta/inbox/signals.jsonl', 'a') as f:
            f.write(json.dumps(signal) + '\n')
        
        # Notify CHAD_YI
        with open('/agents/quanta/outbox/signal-alert.json', 'w') as f:
            json.dump({
                'type': 'trading_signal',
                'signal': signal,
                'source': 'CALLISTOFX',
                'timestamp': datetime.now().isoformat(),
                'action_required': 'review_and_execute'
            }, f, indent=2)
        
        print(f"📁 Signal saved to inbox")
    else:
        print(f"ℹ️ Not a signal message")

print("🔍 Monitoring CALLISTOFX channel...")
print("Press Ctrl+C to stop")

client.start()
client.run_until_disconnected()
```

### Step 5: Run Monitor

```bash
cd /agents/quanta
python callistofx_monitor.py
```

Quanta will now:
- Monitor CALLISTOFX 24/7
- Parse trading signals
- Save to inbox
- Alert when signals arrive

### Step 6: Auto-Execute or Review

Create `/agents/quanta/signal_processor.py`:

```python
import json
import time
from datetime import datetime

def process_signal(signal):
    """Decide whether to auto-execute or ask for approval"""
    
    # High confidence signals (clear format, known pair)
    if signal['pair'] in ['EURUSD', 'GBPUSD', 'XAUUSD']:
        if signal.get('confidence', 0) > 0.8:
            return 'auto_execute'
    
    # Default: ask for approval
    return 'ask_approval'

def execute_trade(signal):
    """Execute trade via OANDA API"""
    # TODO: Implement OANDA execution
    print(f"🚀 Executing {signal['action']} {signal['pair']}")
    print(f"   Entry: {signal['entry']}")
    print(f"   SL: {signal['sl']}")
    print(f"   TP: {signal['tp']}")

def alert_chad_yi(signal, action):
    """Alert CHAD_YI for approval"""
    alert = {
        'type': 'trading_signal_pending',
        'signal': signal,
        'recommended_action': action,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('/agents/quanta/outbox/pending-signal.json', 'w') as f:
        json.dump(alert, f, indent=2)
    
    print(f"📤 Signal sent to CHAD_YI for approval")

# Main loop
while True:
    try:
        with open('/agents/quanta/inbox/signals.jsonl', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            signal = json.loads(line)
            
            decision = process_signal(signal)
            
            if decision == 'auto_execute':
                execute_trade(signal)
            else:
                alert_chad_yi(signal, decision)
        
        # Clear processed signals
        open('/agents/quanta/inbox/signals.jsonl', 'w').close()
        
    except FileNotFoundError:
        pass  # No signals yet
    
    time.sleep(5)  # Check every 5 seconds
```

## Security Notes

⚠️ **Important:**
- `quanta_session.session` file contains your login
- Keep it secure, don't commit to git
- Quanta can only read, not send messages (unless configured)
- Monitor only CALLISTOFX, not personal chats

## Integration with Quanta

Add to Quanta's config:
```json
{
  "telegram_monitor": {
    "enabled": true,
    "channel": "CALLISTOFX",
    "auto_execute": false,  // Set to true for auto-trading
    "pairs_allowed": ["EURUSD", "GBPUSD", "XAUUSD"]
  }
}
```

## Troubleshooting

**"Session file not found"**: Run `telegram_auth.py` first
**"Cannot find channel"**: Check channel ID from step 3
**"Not receiving messages"**: Make sure you're subscribed to CALLISTOFX

## Next Steps

1. Get your Telegram API credentials
2. Run authentication script
3. Find CALLISTOFX channel ID
4. Start monitoring
5. Test with a signal
6. Configure auto-execution or approval workflow