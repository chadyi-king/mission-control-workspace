# Quanta v4.0 - Desktop Installation

## What You Need

1. Python 3.10+ installed
2. Telegram account
3. OANDA API credentials

## Installation Steps

### Step 1: Extract Files
Extract `quanta-v4.0-desktop.zip` to a folder like `C:\quanta` or `~/quanta`

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure OANDA
Edit `.env` file:
```
OANDA_ACCOUNT_ID=001-003-8520002-001
OANDA_API_KEY=your_api_key_here
```

### Step 4: Configure Telegram
Edit `telegram_config.py`:
```python
TELEGRAM_API_ID = your_api_id  # Get from my.telegram.org
TELEGRAM_API_HASH = 'your_api_hash'  # Get from my.telegram.org
PHONE_NUMBER = '+65XXXXXXXX'  # Your phone number
CALLISTOFX_CHANNEL = 'CallistoFx'  # Channel name
```

### Step 5: Authenticate Telegram (ONE TIME)
```bash
python3 -c "
from telethon import TelegramClient
client = TelegramClient('quanta_session', YOUR_API_ID, 'YOUR_API_HASH')
client.start()
print('Authenticated!')
client.disconnect()
"
```
Enter your phone number and the code Telegram sends you.

### Step 6: Run Quanta
```bash
python3 monitor_callistofx.py
```

## What It Does

1. **Connects to Telegram** - Listens to CallistoFx Premium
2. **Parses signals** - Buy/Sell, Entry, SL, TP
3. **Calculates position** - Based on $20 fixed risk per trade
4. **3-Tier Entry** - Enters at high, mid, low of range
5. **Manages trades** - Auto SL management:
   - +20 pips → Move to breakeven
   - +50 pips → Lock +20 pips profit
   - +100 pips → Trail SL at -50 pips

## Risk Settings

Edit these in `monitor_callistofx.py` (TradingState class):
- `initial_balance = 2000` - Your starting balance
- `risk_percent = 2` - 2% per trade ($20 on $2000)
- `max_daily_risk = 6` - 6% max per day
- `max_concurrent_trades = 2`
- `max_trades_per_day = 5`

## Files

- `monitor_callistofx.py` - Main bot (reads Telegram, manages trades)
- `oanda_executor.py` - OANDA API wrapper
- `telegram_config.py` - Telegram credentials
- `.env` - OANDA credentials
- `quanta_session.session` - Telegram auth (auto-created)

## Safety

- Set `AUTO_EXECUTE = False` for paper trading first
- Test with OANDA demo account
- Monitor logs in `logs/` folder
