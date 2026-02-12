# Enhanced Trading Strategy - Risk Management & Profit Maximization

## Original Strategy (Base)
Entry → 10% @ +20, +40, +60, +80, +100 pips
Breakeven SL at +20 pips

## ENHANCED Strategy - Adaptive Risk Management

### 1. DYNAMIC STOP LOSS (Protect Capital)

**Tier 1: Initial SL (Signal Based)**
- Use signal SL as initial (e.g., 2665 for 2680 entry = 15 pips risk)
- Never exceed 2% account risk per trade

**Tier 2: Breakeven Trigger**
- When price hits +20 pips (first TP)
- Move SL to entry + 2 pips (guarantee profit)
- Lock in minimum +2 pips if reverses

**Tier 3: Trailing SL (Profitable Positions)**
- After +50 pips profit: Trail SL at -30 pips from current
- After +100 pips: Trail SL at -50 pips from current
- Never let winner turn to loser beyond +20 pips

**Tier 4: Time-Based Exit**
- If trade open > 4 hours with < +10 pips: Close at market
- Capital better deployed elsewhere

### 2. ADAPTIVE TAKE PROFIT (Maximize Gains)

**Market Condition Detection:**
```
Strong Trend (ADX > 25):
  - Hold 50% position for extended run
  - TP levels: 10% @ +20, 10% @ +50, 30% @ +100, 50% runner

Ranging Market (ADX < 20):
  - Quick profits, tight exits
  - TP levels: 20% @ +20, 30% @ +40, 50% @ +60

Volatile (ATR > 2x average):
  - Wider SL, wider TP
  - TP levels: 10% @ +30, 20% @ +60, 30% @ +100, 40% runner
```

**Chart Pattern Recognition:**
- If price approaches resistance: Take profit early
- If breakout confirmed: Extend runner to +200 pips
- If divergence on RSI: Exit full position

### 3. SIGNAL QUALITY SCORING

**Base Score (0-100):**
- Signal quality from group: +40 points
- Time of day (London/NY session): +20 points
- Price action alignment: +20 points
- Trend direction match: +20 points

**Trade Size Based on Score:**
```
Score 80-100: Full position size
Score 60-79: 75% position size
Score 40-59: 50% position size
Score < 40: Skip trade
```

### 4. PARTIAL PROFIT LADDER (Revised)

**Conservative (Score < 70):**
- 25% @ +20 pips
- 25% @ +40 pips
- 25% @ +60 pips
- 25% runner with trailing SL

**Aggressive (Score >= 70):**
- 10% @ +20 pips (cover risk)
- 20% @ +50 pips
- 30% @ +100 pips
- 40% runner to +200/+300 pips

### 5. RUNNER POSITION MANAGEMENT

**The 40-50% runner is where big profits come from:**

**Trailing Rules:**
- At +50 pips: SL at entry (breakeven)
- At +100 pips: SL at +50 (lock 50 pips)
- At +150 pips: SL at +100 (lock 100 pips)
- At +200 pips: Move SL to +150, let it run
- Close if reversal candle forms

**Exit Signals for Runner:**
- RSI overbought/oversold (>80 or <20)
- Divergence on MACD
- Price hits major resistance/support
- Volume drops significantly
- Opposite signal from same channel

### 6. RISK:REWARD RATIO ENFORCEMENT

**Minimum 1:2 R:R Required:**
- If SL is 15 pips, minimum TP is 30 pips
- If signal offers 1:1.5, reduce position size or skip
- Never take trade with R:R < 1:1.5

### 7. CORRELATION CHECK

**Before Taking Trade:**
- Check if correlated pairs already in profit
- Example: Long XAUUSD + Long EURUSD = Double risk on USD weakness
- Max 2 correlated positions open simultaneously

### 8. SESSION-BASED ADJUSTMENTS

**Asian Session (Low Volatility):**
- Reduce position size by 50%
- Take profits earlier (+40 pips max)
- Wider SL (1.5x normal)

**London Session (High Volatility):**
- Full position size
- Extended runners (+150-200 pips)
- Tighter SL management

**NY Session (Mixed):**
- Check for news calendar
- Reduce size if high-impact news upcoming
- Close before major announcements

### 9. AGENT DECISION LOGIC

**When Signal Arrives:**
1. Parse signal (symbol, entry, SL, TP)
2. Calculate R:R ratio (must be >= 1:2)
3. Assess market conditions (trend, volatility)
4. Calculate position size (based on score)
5. Set initial SL from signal
6. Execute entry
7. Set TP1 at +20 pips (10-25% depending on score)
8. Move SL to breakeven when TP1 hits
9. Continue ladder based on market condition
10. Trail runner with dynamic SL

**Real-Time Monitoring:**
- Check every 5 minutes
- Update trailing SL
- Monitor for exit signals
- Log all actions

### 10. LOGGING & REVIEW

**Every Trade Logged:**
- Entry price, time, size
- Signal score
- Market condition
- SL/TP levels hit
- Final P&L
- Mistakes (if any)

**Weekly Review:**
- Which signal types perform best?
- Which TP levels most effective?
- Adjust strategy based on data

## EXAMPLE TRADE

**Signal:** XAUUSD buy 2680, SL 2665, TP open
**Analysis:**
- Score: 85 (strong trend, London session, good PA)
- SL: 15 pips
- R:R: Can achieve 1:10+ with runner

**Execution:**
- Position size: 100% (score 85)
- Entry: 2680
- Initial SL: 2665 (-15 pips)

**Management:**
- TP1 (+20 pips): Close 10% at 2700, move SL to 2682
- TP2 (+50 pips): Close 20% at 2730, move SL to 2700
- TP3 (+100 pips): Close 30% at 2780, move SL to 2750
- Runner (40%): Trail SL at -50 pips from price
- Exit runner at +180 pips (divergence spotted)

**Result:** 
- 10% @ +20 pips
- 20% @ +50 pips
- 30% @ +100 pips
- 40% @ +180 pips
- Weighted average: +97 pips per unit
- Risk: 15 pips
- R:R: 6.5:1
