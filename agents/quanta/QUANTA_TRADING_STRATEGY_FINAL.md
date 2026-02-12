# QUANTA TRADING STRATEGY (FINAL - COMMITTED)
## Date: 2026-02-13 01:42
## Status: CORRECT AND FINAL

**THIS IS THE STRATEGY. DO NOT FORGET. REFERENCE THIS FILE.**

---

## 1. RISK MANAGEMENT

**Fixed Risk:** $20 per trade (first 20 trades)
- After 20 successful trades, can increase
- Never risk more than 2% of account normally
- Position size calculated to risk exactly $20

---

## 2. ENTRY STRATEGY (3-Tier DCA)

**Signal Format:** XAUUSD BUY 2680-2685, SL: 2675

**3-Tier Entry:**
| Tier | % of Position | Entry Price | When |
|------|---------------|-------------|------|
| Tier 1 | 33% | High of range (2685) | Price hits high |
| Tier 2 | 33% | Mid of range (2682.5) | Price drops to mid |
| Tier 3 | 34% | Low of range (2680) | Price drops to low |

**Position Sizing Example:**
- Account: $10,000
- Risk: $20 fixed
- Entry mid: 2682.5
- SL: 2675
- Risk pips: 7.5
- Position: 0.267 lots total
- Tier 1: 0.088 lots @ 2685
- Tier 2: 0.088 lots @ 2682.5
- Tier 3: 0.091 lots @ 2680

---

## 3. STOP LOSS MANAGEMENT

**Initial SL:** Signal's SL (e.g., 2675)

**At +20 pips profit:**
- Move SL to entry (breakeven)
- Now can't lose money

**At +100 pips (runner start):**
- Keep SL at breakeven until +100
- At +100: Start trailing 100 pips behind

**Trailing Logic:**
- Price at +100: SL at +0 (breakeven)
- Price at +150: SL at +50
- Price at +200: SL at +100
- Price at +300: SL at +200
- Always 100 pips behind current price

---

## 4. TAKE PROFIT STRATEGY

### Phase 1: Standard TPs (First 50%)
| Level | Pips | Close % | Cumulative Closed |
|-------|------|---------|-------------------|
| TP1 | +20 | 10% | 10% |
| TP2 | +40 | 10% | 20% |
| TP3 | +60 | 10% | 30% |
| TP4 | +80 | 10% | 40% |
| TP5 | +100 | 10% | 50% |

**After TP5:** 50% remains (RUNNER)

### Phase 2: Runner Management (Last 50%)
**Activation:** At +100 pips

**Every +50 pips beyond +100:**
- Close 10% of whatever is LEFT (not original)
- Move SL up (100 pips behind price)

**Example Runner Progression:**
```
At +100 pips: Runner = 50% of position active

+150 pips:
- Close: 10% of 50% = 5% of original position
- Remaining: 45%
- SL: +50 (100 pips behind price)

+200 pips:
- Close: 10% of 45% = 4.5% of original
- Remaining: 40.5%
- SL: +100 (100 pips behind price)

+250 pips:
- Close: 10% of 40.5% = 4.05% of original
- Remaining: 36.45%
- SL: +150

... continues until SL hit
```

**Goal:** Capture big moves (100-6000+ pips)
- Take profits along the way (10% every +50 pips)
- Keep most position running
- SL protects profits (trailing 100 pips)

---

## 5. AUTOMATED SL MOVES

**Detect messages like:**
- "Move SL to BE"
- "Shift SL to breakeven"
- "SL to entry"
- "Protect profits"

**Execute automatically:**
- Parse message
- Identify action
- Modify SL in OANDA
- Log the change

---

## 6. LEARNING SYSTEM

**Read ALL messages (not just signals):**
- Trader commentary
- Market analysis
- Pattern changes
- Sentiment shifts

**What to learn:**
- How trader thinks
- When to expect signals
- What "strong trend" means
- When to be cautious

**Store learning:**
- agents/quanta/learning_db.json
- Update with patterns
- Improve signal detection
- Adapt to trader style changes

---

## 7. EXECUTION PRIORITY

**FAST (Immediate):**
1. Detect signal
2. Calculate position
3. Execute 3-tier entry
4. Set SL

**ONGOING (Monitor):**
1. Track price movement
2. Move SL at +20 pips
3. Close partial at TPs
4. Activate runner at +100
5. Manage runner (every +50 pips)

**RESPONSIVE (Messages):**
1. Read all messages
2. Detect SL move commands
3. Execute immediately
4. Learn from commentary

---

## 8. OANDA INTEGRATION

**API Functions Needed:**
- `create_order()` - Enter position
- `modify_sl()` - Move stop loss
- `close_partial()` - Close portion of position
- `get_positions()` - Monitor open trades
- `get_price()` - Current market price

**Execution Flow:**
```
Signal detected
  ↓
Calculate size ($20 risk)
  ↓
Create 3 orders (Tier 1, 2, 3)
  ↓
Set SL
  ↓
Monitor price
  ↓
At +20: Modify SL to BE
  ↓
At TPs: Close partial
  ↓
At +100: Activate runner
  ↓
Every +50: Close 10% of runner, trail SL
  ↓
Until SL hit or fully closed
```

---

## 9. TESTING CHECKLIST

**Before Live Trading:**
- [ ] Test on demo account
- [ ] Verify $20 risk calculation
- [ ] Test 3-tier entry
- [ ] Test SL moves
- [ ] Test TP closes
- [ ] Test runner activation
- [ ] Test trailing SL
- [ ] Test message detection
- [ ] Test for 10+ trades
- [ ] Verify P&L tracking

---

## 10. REMINDERS

**If Caleb asks about strategy:**
- Reference this file
- Explain: $20 risk, 3-tier entry, 5 TPs, runner
- Show example numbers

**If I forget:**
- Read this file
- Ask Caleb: "Reference QUANTA_TRADING_STRATEGY_FINAL.md"

**If strategy needs update:**
- Caleb must approve changes
- Document change in CHANGELOG
- Update this file
- Version bump (v4.0 → v4.1)

---

*This is THE strategy. Do not deviate without approval.*
*Last updated: 2026-02-13 01:42 SGT*
*Status: FINAL AND COMMITTED*
OANDA_LIVE_ACCOUNT=001-003-8520002-001
OANDA_BALANCE=2004.57 SGD
RISK_PER_TRADE=20 (first 20 trades)
