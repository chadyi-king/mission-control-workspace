# Telegram Bridge - CHAD_YI ↔ Kimi-Claw-Helios
## Simplest communication method

---

## How It Works

```
Kimi-Claw-Helios (kimi.com)
    ↓
Sends Telegram message
    ↓
CHAD_YI (OpenClaw) receives it
    ↓
CHAD_YI decides & responds
    ↓
Optional: Kimi executes browser task
```

---

## Step 1: Add Kimi Claw to Your Telegram

1. In Kimi Claw, run:
```bash
# Get Telegram bot token from BotFather
# Or use Kimi's built-in Telegram integration
```

2. Add Kimi Claw bot to this chat (512366713)

---

## Step 2: Message Format

### Kimi Sends to CHAD_YI:
```
🤖 Kimi-Claw-Helios Alert

Type: trading_signal
Time: 15:30:00 SGT

Signal:
XAUUSD BUY
Entry: 4970-4975
SL: 4965
TP: 4990/5000/5010/5020

Screenshot: [attached]

Execute trade? (reply: yes/no)
```

### CHAD_YI Responds:
```
✅ EXECUTING TRADE

Order: XAUUSD BUY 100 units
Entry: Market (4977)
SL: 4965
TP: 4990

Status: PENDING
```

---

## Step 3: Kimi Claw Script

Add this to Kimi Claw:

```python
# In Kimi Claw workspace: alert_chad_yi.py

import requests

def alert_chad_yi(signal_data, screenshot_path=None):
    """Send alert to CHAD_YI via Telegram"""
    
    CHAD_YI_CHAT_ID = "512366713"
    
    message = f"""🤖 Kimi-Claw-Helios Alert

Type: {signal_data['type']}
Time: {signal_data['timestamp']}

Signal:
{signal_data['symbol']} {signal_data['direction']}
Entry: {signal_data['entry']}
SL: {signal_data['sl']}
TP: {signal_data['tps']}

Awaiting decision..."""
    
    # Send via Telegram
    telegram.send(
        to=CHAD_YI_CHAT_ID,
        text=message,
        media=screenshot_path  # if available
    )
    
    print(f"Alert sent to CHAD_YI: {signal_data['symbol']}")

# Example usage
if __name__ == "__main__":
    signal = {
        "type": "trading_signal",
        "timestamp": "15:30:00",
        "symbol": "XAUUSD",
        "direction": "BUY",
        "entry": "4970-4975",
        "sl": "4965",
        "tps": ["4990", "5000", "5010", "5020"]
    }
    alert_chad_yi(signal, "/path/to/screenshot.png")
```

---

## Step 4: CHAD_YI Receives

When I receive the message, I'll:

1. Parse the signal
2. Check OANDA account
3. Calculate position size
4. Execute trade if approved
5. Report back to you

**No HTTP endpoint needed** - just Telegram messages.

---

## Alternative: File-Based (If Telegram doesn't work)

Kimi writes to file → CHAD_YI polls file

**In Kimi Claw:**
```python
# Write signal to shared location
with open("/shared/signals/incoming/new_signal.json", "w") as f:
    json.dump(signal_data, f)
```

**In CHAD_YI:**
- Poll every 30 seconds for new files
- Process when found
- Move to processed folder

---

## Recommendation

**Use Telegram** - it's instant and already works.

**Want me to create the full Kimi Claw script for this?**