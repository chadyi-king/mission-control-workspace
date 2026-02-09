# Quanta Trading Setup

## Required Access (URGENT)

### 1. Telegram Account Access
**Purpose:** Read trading signals from channels
**Needs:**
- Telegram API credentials (api_id, api_hash)
- Bot token for @MensaMusaTradingBot
- Access to signal channels

### 2. TradingView
**Purpose:** Chart analysis, alerts, backtesting
**Needs:**
- TradingView account (free or paid)
- API access for alerts (webhooks)
- Pine Script knowledge

### 3. Trading Accounts

#### OANDA (Forex)
**Status:** ⏳ PENDING SETUP
**Needs:**
- Account creation
- API key generation
- Practice account for testing

#### Moomoo (Options/Stocks)
**Status:** ⏳ PENDING SETUP
**Needs:**
- Account verification
- API access request
- Paper trading for testing

## Initial Strategy (MVP)

### Phase 1: Signal Monitoring
1. Monitor Telegram signal channels
2. Parse signals (entry, stop-loss, take-profit)
3. Log to database
4. Send alerts to user

### Phase 2: Automated Execution
1. Connect to OANDA API
2. Execute forex trades automatically
3. Risk management (max 2% per trade)
4. Position tracking

### Phase 3: Options Flow
1. Monitor Twitter for options flow
2. Connect to Moomoo API
3. Execute options trades
4. Advanced risk management

## Risk Parameters (MANDATORY)
- Max 2% risk per trade
- Daily loss limit: 5%
- Weekly loss limit: 10%
- No trading during high-impact news
- Position size based on volatility

## Files to Create
- SECRETS.md (API keys - encrypted)
- strategies/breakout.md
- strategies/trend-following.md
- backtests/performance-log.md