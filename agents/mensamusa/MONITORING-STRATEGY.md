# A5-2 Options Flow Monitoring
**MensaMusa v2.0 - Awaiting Moomoo Credentials**

## Strategy Overview
**Source:** Twitter/X options flow accounts
**Execution:** Moomoo options trading
**Focus:** Unusual options activity, sweeps, block trades

## Implementation Plan

### Phase 1: Twitter Monitoring
- Monitor accounts: @unusual_whales, @OptionsFlow, etc.
- Parse options flow alerts
- Extract: ticker, strike, expiry, volume, premium

### Phase 2: Analysis
- Check if flow is bullish/bearish
- Verify against open interest
- Cross-reference with recent news
- Calculate risk/reward

### Phase 3: Alerts
- High conviction plays → Alert CHAD_YI
- Unusual activity → Log for review
- Earnings plays → Flag with date

### Phase 4: Execution (Optional)
- Small test positions on high conviction
- Strict risk management
- Quick exits on reversals

## Technical Stack
- Python 3.10+
- Tweepy for Twitter API
- Moomoo OpenAPI
- pandas for flow analysis
- asyncio for real-time monitoring

## Example Flow Alert
```
$AAPL
$200 CALLS
EXPIRY: 2/16
PREMIUM: $2.5M
UNUSUAL VOLUME
```

## Watchlist
- AAPL, TSLA, NVDA, MSFT, AMZN
- SPY, QQQ, IWM
- Meme stocks: GME, AMC

## Next Steps
1. Provide Moomoo account credentials
2. Set up Twitter API access
3. Configure watchlist
4. Define alert thresholds

**Status:** Ready to monitor once credentials received.
