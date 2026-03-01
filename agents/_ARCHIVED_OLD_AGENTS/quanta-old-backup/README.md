# Quanta v4.1 - Desktop Installation

## What You Need

1. Python 3.10+ installed
2. Telegram account
3. OANDA API credentials

## Installation Steps

### Step 1: Extract Files
Extract `quanta-v4.1-desktop.tar.gz` to a folder like `C:\quanta` or `~/quanta`

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
3. **LEARNS from every message** - Patterns, analysis, reasoning
4. **Tracks recurring strategies** - Identifies their core teaching topics
5. **Calculates position** - Based on $20 fixed risk per trade
6. **3-Tier Entry** - Enters at high, mid, low of range
7. **Manages trades** - Auto SL management:
   - +20 pips → Move to breakeven
   - +50 pips → Lock +20 pips profit
   - +100 pips → Trail SL at -50 pips
8. **Tracks outcomes** - Records wins/losses per pattern
9. **Reports learning** - Weekly performance by pattern + recurring strategies

## Risk Settings

Edit these in `monitor_callistofx.py` (TradingState class):
- `initial_balance = 2000` - Your starting balance
- `risk_percent = 2` - 2% per trade ($20 on $2000)
- `max_daily_risk = 6` - 6% max per day
- `max_concurrent_trades = 2`
- `max_trades_per_day = 5`

## Learning System

### Pattern Recognition
Quanta reads EVERY message and extracts:

| Pattern | Example | Tracked |
|---------|---------|---------|
| `engulfing` | "Bullish engulfing at support" | ✅ |
| `pin_bar` | "Pin bar rejection" | ✅ |
| `support_bounce` | "Bouncing off daily support" | ✅ |
| `rsi_oversold` | "RSI oversold" | ✅ |
| `breakout` | "Breaking consolidation" | ✅ |

### Strategy Tracking
**When they discuss the same strategy multiple times, Quanta recognizes it:**

```
📚 NEW RECURRING STRATEGY: 'smart_money_concepts' mentioned 3+ times
⭐ CORE STRATEGY IDENTIFIED: 'supply_demand' mentioned 5+ times
```

**20 Strategy Keywords Tracked:**
- `smart_money_concepts` - SMC, imbalance, order blocks
- `supply_demand` - Supply/demand zones
- `price_action` - Pure price action
- `breakout_strategy` - Breakout trading
- `pullback_strategy` - Pullback entries
- `trend_following` - Trend following
- `mean_reversion` - Mean reversion
- `momentum` - Momentum trading
- `scalping` - Scalp trades
- `swing_trading` - Swing trades
- `london_breakout` - London session breakout
- `ny_session` - New York session trades
- `asia_range` - Asia range setups
- `kill_zone` - Kill zone timing
- `judas_swing` - Judas swing pattern
- `stop_hunt` - Stop hunt setups
- `choch` - Change of character
- `bos` - Break of structure
- `inducement` - Inducement patterns

### Learning Reports:
Every day at 8 PM, Quanta generates:
```
🧠 WEEKLY LEARNING REPORT
Period: Last 7 days
Total Trades: 15 | Wins: 10 | Losses: 5
Total P&L: +$320.50

📚 RECURRING STRATEGIES (mentioned 3+ times):
   • smart_money_concepts: mentioned 8 times ⭐ CORE
   • supply_demand: mentioned 6 times ⭐ CORE
   • london_breakout: mentioned 4 times

⭐ CORE STRATEGIES (mentioned 5+ times - their main approach):
   • smart_money_concepts: 8 mentions
     Example: "Using SMC concepts, we identified an order block..."
   • supply_demand: 6 mentions
     Example: "Price rejecting from supply zone..."

✅ BEST PATTERNS (70%+ win rate):
   • engulfing: 80% (4W/1L) | P&L: +$180.00
   • support_bounce: 75% (3W/1L) | P&L: +$120.00

⚠️ AVOID PATTERNS (40%- win rate):
   • news_driven: 33% (1W/2L) | P&L: -$60.00
```

## Files

- `monitor_callistofx.py` - Main bot v4.1 (trading + learning)
- `oanda_executor.py` - OANDA API wrapper
- `telegram_config.py` - Telegram credentials
- `.env` - OANDA credentials
- `learning_database.json` - Tracks patterns, strategies, outcomes
- `lessons_learned.jsonl` - Log of all lessons
- `quanta_session.session` - Telegram auth (auto-created)

## Output Files Created:

- `trade_alerts.jsonl` - All trade alerts
- `open_trades.json` - Currently open trades
- `trading_state.json` - Daily stats and balance
- `learning_database.json` - Pattern performance + strategy mentions
- `learning_database_lessons.jsonl` - Educational content log

## Safety

- Set `AUTO_EXECUTE = False` for paper trading first
- Test with OANDA demo account
- Monitor logs in console
- Review learning reports to see which patterns work best
- See which strategies they teach most (their core approach)
