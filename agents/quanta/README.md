# Quanta v4.0 - Desktop Installation

## What You Need

1. Python 3.10+ installed
2. Telegram account
3. OANDA API credentials

## Installation Steps

### Step 1: Extract Files
Extract `quanta-v4.0-desktop.tar.gz` to a folder like `C:\quanta` or `~/quanta`

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
TELEGRAM_API_ID = 32485688  # Get from my.telegram.org
TELEGRAM_API_HASH = 'your_api_hash_here'  # From my.telegram.org
PHONE_NUMBER = '+65XXXXXXXX'  # Your phone with country code
CALLISTOFX_CHANNEL = '🚀 CallistoFx Premium Channel 🚀'
```

### Step 5: Authenticate Telegram (ONE TIME)
```bash
python3 -c "
from telethon import TelegramClient
client = TelegramClient('quanta_session', 32485688, 'your_api_hash')
client.start()
print('Authenticated!')
client.disconnect()
"
```
Enter your phone number, then enter the code Telegram sends you.

### Step 6: Run Quanta
```bash
python3 monitor_callistofx.py
```

## What It Does

1. **Connects to Telegram** - Listens to CallistoFx Premium
2. **Parses signals** - Buy/Sell, Entry, SL, TP
3. **LEARNS from messages** - Extracts patterns, analysis, reasoning
4. **Calculates position** - Based on $20 fixed risk per trade
5. **3-Tier Entry** - Enters at high, mid, low of range
6. **Manages trades** - Auto SL management:
   - +20 pips → Move to breakeven
   - +50 pips → Lock +20 pips profit
   - +100 pips → Trail SL at -50 pips
7. **Tracks outcomes** - Records wins/losses per pattern
8. **Reports learning** - Weekly performance by pattern

## Risk Settings

Edit these in `monitor_callistofx.py` (TradingState class):
- `initial_balance = 2000` - Your starting balance
- `risk_percent = 2` - 2% per trade ($20 on $2000)
- `max_daily_risk = 6` - 6% max per day
- `max_concurrent_trades = 2`
- `max_trades_per_day = 5`

## Learning System

Quanta reads EVERY message from the channel and learns:

### Patterns Tracked:
- `engulfing` - Bullish/Bearish engulfing candles
- `pin_bar` - Pin bars, shooting stars, hammers
- `doji` - Doji patterns
- `support_bounce` - Price bouncing off support
- `resistance_break` - Breaking through resistance
- `trend_continuation` - Trend continuation setups
- `trend_reversal` - Trend reversal setups
- `rsi_oversold` - RSI oversold conditions
- `rsi_overbought` - RSI overbought conditions
- `macd_cross` - MACD crossovers
- `ema_bounce` - EMA bounce setups
- `consolidation_break` - Breaking out of consolidation
- `news_driven` - News-based trades (FOMC, NFP, CPI, PMI)

### Analysis Extracted:
- Any text after "Analysis:", "Why:", "Reason:", "Setup:"
- Pattern explanations
- Market context (London/NY/Asia session)
- Confidence levels (High/Medium/Low)

### Learning Reports:
Every day at 8 PM, Quanta generates a report:
```
🧠 WEEKLY LEARNING REPORT
Period: Last 7 days
Total Trades: 15 | Wins: 10 | Losses: 5
Total P&L: +$320.50

✅ BEST PATTERNS (70%+ win rate):
   • engulfing: 80% (4W/1L) | P&L: +$180.00
   • support_bounce: 75% (3W/1L) | P&L: +$120.00

⚠️ AVOID PATTERNS (40%- win rate):
   • news_driven: 33% (1W/2L) | P&L: -$60.00
```

## Files

- `monitor_callistofx.py` - Main bot (reads Telegram, manages trades, learns)
- `oanda_executor.py` - OANDA API wrapper
- `telegram_config.py` - Telegram credentials
- `.env` - OANDA credentials
- `learning_database.json` - Tracks patterns and outcomes
- `lessons_learned.jsonl` - Log of all lessons
- `quanta_session.session` - Telegram auth (auto-created)

## Output Files Created:

- `trade_alerts.jsonl` - All trade alerts
- `open_trades.json` - Currently open trades
- `trading_state.json` - Daily stats and balance
- `learning_database.json` - Pattern performance stats
- `learning_database_lessons.jsonl` - Educational content log

## Safety

- Set `AUTO_EXECUTE = False` for paper trading first
- Test with OANDA demo account
- Monitor logs in console
- Review learning reports to see which patterns work best
