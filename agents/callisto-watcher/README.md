# CallistoFX Telegram Watcher

## Purpose
24/7 automated watcher for Caleb's personal Telegram account to monitor CallistoFX trading signals.

## How It Works
1. Connects to Caleb's personal Telegram via MTProto (not bot API)
2. Monitors "🚀 CallistoFx Premium Channel 🚀" for signals
3. Parses trading signals (pair, direction, entry, SL, TP)
4. Sends parsed signals to Redis channel `callisto→quanta`
5. Runs 24/7 on Render with auto-restart

## Setup (One-Time)

### Step 1: Generate Session String
```bash
cd /agents/callisto-watcher
pip install -r requirements.txt
python session_generator.py
```

Enter your phone number when prompted, then enter the Telegram code you receive.

This creates `session.txt` containing your encrypted session string.

### Step 2: Deploy to Render
```bash
# Push to GitHub
git add .
git commit -m "Add Callisto watcher"
git push

# Deploy on Render (free tier)
# - Connect GitHub repo
# - Use render.yaml for config
# - Set environment variables
```

## Environment Variables
```bash
REDIS_URL=rediss://default:PASSWORD@national-gar-36005.upstash.io:6379
TELEGRAM_SESSION=<from session.txt>
TARGET_CHANNEL="🚀 CallistoFx Premium Channel 🚀"
```

## Signal Format Sent to Redis
```json
{
  "from": "callisto",
  "to": "quanta",
  "type": "signal",
  "timestamp": "2026-02-18T23:30:00+08:00",
  "signal": {
    "pair": "EURUSD",
    "direction": "BUY",
    "entry": 1.0850,
    "stop_loss": 1.0800,
    "take_profit": 1.0900,
    "raw_message": "..."
  }
}
```

## Files
- `session_generator.py` - One-time auth to generate session string
- `watcher.py` - Main 24/7 watcher service
- `requirements.txt` - Python dependencies
- `render.yaml` - Render deployment configuration

## Monitoring
The watcher reports its status to Redis channel `callisto→helios` every 5 minutes.

## Auto-Restart
Render free tier includes auto-restart on crash. The watcher also has internal error handling and reconnection logic.
