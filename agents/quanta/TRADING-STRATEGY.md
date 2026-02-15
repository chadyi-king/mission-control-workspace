# A5-1 Trading Strategy: Forex/Commodities
**Quanta v2.0 - Awaiting OANDA Credentials**

## Strategy Overview
**Signal Source:** Telegram channels
**Execution:** OANDA API
**Markets:** Forex pairs (EUR/USD, GBP/USD), Gold (XAU/USD), Commodities

## Implementation Plan

### Phase 1: Telegram Integration
- Monitor configured Telegram channels
- Parse signal messages (entry, SL, TP)
- Validate signal format

### Phase 2: Risk Management
- Position sizing: 1-2% per trade
- Max daily loss: 5%
- Correlation check: Avoid overexposure

### Phase 3: Execution
- Validate signal quality score
- Check market hours/liquidity
- Place orders via OANDA REST API
- Set SL/TP automatically

### Phase 4: Monitoring
- Track open positions
- Monitor margin usage
- Daily P&L reporting

## Technical Stack
- Python 3.10+
- OANDA v20 REST API
- python-telegram-bot
- pandas for analysis
- asyncio for concurrent ops

## Signal Format Expected
```
PAIR: EUR/USD
ACTION: BUY
ENTRY: 1.0850
SL: 1.0820
TP1: 1.0880
TP2: 1.0910
```

## Next Steps
1. Provide OANDA API key
2. Provide OANDA account ID
3. Configure Telegram bot token
4. Set signal channels to monitor

**Status:** Ready to deploy once credentials received.
