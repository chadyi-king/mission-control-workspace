# Quanta-v2 Trading Bot
## Complete Trading System (No Telegram Yet)

## Strategy Summary
- **Risk:** $20 fixed for first 20 trades, then 1-2% of account
- **Entry:** 3-tier split (33%/33%/34% at high/mid/low of range)
- **TPs:** 5 levels (+20, +40, +60, +80, +100 pips), close 10% each
- **Runner:** After +100 pips, trail SL 100 pips behind, close 10% of remaining every +50 pips
- **SL:** BE at +20, lock +20 at +50, trail at +100

## Files
- `config.py` - Settings
- `risk_manager.py` - Position sizing
- `oanda_client.py` - OANDA API
- `trade_manager.py` - Trade execution & management
- `signal_parser.py` - Parse signals
- `learning_engine.py` - Learn from commentary
- `reporter.py` - Report to Helios
- `main.py` - Main loop

## Setup
1. Set OANDA_API_TOKEN and OANDA_ACCOUNT_ID in .env
2. Deploy to Render
3. Test with manual signals first
4. Add Telegram monitoring later
