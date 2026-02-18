# QUANTA BUILD PLAN FOR HELIOS
**Complete Rebuild Specification**  
**Date:** Feb 18, 2026  
**Status:** Reference Previous Build + New Requirements

---

## 🎯 WHAT WAS BUILT BEFORE (Reference)

### Previous Quanta Files (in `/agents/quanta/`):

| File | Purpose | Status |
|------|---------|--------|
| `monitor_callistofx.py` | MAIN BOT - Telegram monitor + OANDA executor | ✅ Working code |
| `oanda_executor.py` | OANDA API wrapper - create/modify/close orders | ✅ Working code |
| `oanda_bot.py` | Alternative OANDA implementation | ✅ Backup |
| `quanta_trading.py` | Trading logic and signal processing | ✅ Working |
| `quanta_simple.py` | Simplified version | ✅ Working |
| `telegram_config.py` | API keys and channel settings | ⚠️ Needs token |
| `QUANTA_TRADING_STRATEGY_FINAL.md` | COMPLETE strategy documentation | ✅ Reference |

### What Previous Quanta Did:
1. ✅ Connected to Telegram (CallistoFX channel)
2. ✅ Parsed signals (XAUUSD, forex pairs)
3. ✅ Calculated position sizes ($20 risk)
4. ✅ Executed 3-tier split entry
5. ✅ Monitored open trades
6. ✅ Moved SL to breakeven at +20 pips
7. ✅ Locked profits at +50 pips
8. ✅ Activated runner at +100 pips
9. ✅ Trailed SL (100 pips behind price)
10. ✅ Closed partial at TPs
11. ✅ Reported P&L to dashboard

---

## 🔴 CORRECTED STRATEGY (What You Need to Build)

### What I Got Wrong Before:

| Incorrect (Before) | Correct (Now) |
|-------------------|---------------|
| Max 3 trades/day | **NO LIMIT** on trade count |
| Max 2 concurrent | **NO LIMIT** on concurrent trades |
| Just execute signals | **LEARN** from trader commentary |
| Fixed symbol list | **ANY symbol** channel provides |
| Basic TP strategy | **Multiple profit + Runner strategy** |

### ✅ CORRECT STRATEGY FOR NEW QUANTA:

---

## 1. TELEGRAM MONITORING (CRITICAL)

**Not just signals - READ EVERYTHING:**

```
What to monitor:
✅ Signal messages: "XAUUSD BUY 2680-2685, SL: 2675"
✅ Commentary: "Strong trend forming, looking for breakout"
✅ Analysis: "Support at 2675 held, bullish continuation"
✅ Updates: "Move SL to BE" / "Taking partial profits"
✅ Sentiment: "Risk-off environment, gold bullish"
```

**Learning Database:**
- Store trader patterns
- Learn when signals typically come
- Understand "strong trend" vs "weak trend"
- Adapt to trader style changes

**Files:**
- `learning_database.json` - Pattern storage
- `lessons_learned.jsonl` - Continuous learning

---

## 2. SIGNAL PARSING

**Signal Format Examples:**
```
XAUUSD BUY 2680-2685, SL: 2675, TP1: 2690, TP2: 2700
EURUSD SELL 1.0850-1.0860, SL: 1.0875
BTCUSD BUY 45000-45500, SL: 44500
```

**Parse:**
- Symbol (XAUUSD, EURUSD, etc.)
- Direction (BUY/SELL)
- Entry range (high-low)
- Stop Loss
- Take Profits (if provided)

---

## 3. POSITION SIZING (CRITICAL - CHECK PIP VALUE)

**Formula:**
```
Units = Risk Amount ÷ (Pip Value × SL Distance)
```

**Pip Values (Per Standard Lot):**
| Symbol | Pip Value (SGD) | Lot Size |
|--------|----------------|----------|
| XAUUSD | ~$1.19 | 100 units |
| XAGUSD | ~$0.15 | 100 units |
| EURUSD | ~$13.50 | 100,000 units |
| GBPUSD | ~$17.00 | 100,000 units |
| USDJPY | ~$11.00 | 100,000 units |

**Example (XAUUSD):**
- Risk: $20
- Entry: 2682.5
- SL: 2675
- Distance: 7.5 pips
- Pip value: $1.19
- Calculation: $20 ÷ ($1.19 × 7.5) = 2.24 lots
- Total units: 224

**⚠️ MUST query OANDA for live pip values before calculating!**

---

## 4. 3-TIER SPLIT ENTRY

**Divide position into 3 orders:**

| Tier | % of Position | Entry | When |
|------|---------------|-------|------|
| Tier 1 | 33% | High of range | Price hits high first |
| Tier 2 | 33% | Mid of range | Price drops to mid |
| Tier 3 | 34% | Low of range | Price drops to low |

**Why:** Improves average entry price

---

## 5. TAKE PROFIT STRATEGY (MULTIPLE PROFITS + RUNNER)

### Phase 1: Multiple TPs (First 50% of position)

| TP Level | Pips | Close % | Action |
|----------|------|---------|--------|
| TP1 | +20 | 10% | Close 10%, move SL to BE |
| TP2 | +40 | 10% | Close 10% |
| TP3 | +60 | 10% | Close 10% |
| TP4 | +80 | 10% | Close 10% |
| TP5 | +100 | 10% | Close 10%, **ACTIVATE RUNNER** |

**After TP5:** 50% of position remains → **RUNNER**

### Phase 2: Runner Strategy (Last 50%)

**Activation:** When price hits +100 pips

**Runner Rules:**
1. **Every +50 pips beyond +100:**
   - Close 10% of **REMAINING** position
   - Trail SL (100 pips behind current price)

2. **Example Progression:**
```
+100 pips: Runner active (50% remaining)
+150 pips: Close 10% of 50% = 5%, Remaining: 45%
           SL moved to +50 (100 pips behind)
+200 pips: Close 10% of 45% = 4.5%, Remaining: 40.5%
           SL moved to +100
+250 pips: Close 10% of 40.5% = 4.05%, Remaining: 36.45%
           SL moved to +150
+300 pips: Close 10% of 36.45% = 3.645%, Remaining: 32.8%
           SL moved to +200
... continues until SL hit
```

**Goal:** Capture BIG moves (100-6000+ pips)
- Take profits along the way
- Keep runner going with trailing SL
- Let winners run

---

## 6. STOP LOSS MANAGEMENT

| Price Level | SL Action | Position |
|-------------|-----------|----------|
| +20 pips | Move SL to entry (breakeven) | All |
| +50 pips | Lock +20 pips profit | All |
| +100 pips | Start trailing (100 pips behind) | Runner only |
| Every +50 after | Trail SL, close 10% of runner | Runner only |

**Trailing Logic:**
- Current price: +200
- SL position: +100 (100 pips behind)
- If price drops to +100: Runner stopped out
- If price goes to +300: SL moves to +200

---

## 7. AUTOMATED MESSAGE DETECTION

**Detect and execute commands:**

```
"Move SL to BE" → Move all SLs to entry price
"SL to entry" → Same as above
"Shift SL to breakeven" → Same
"Protect profits" → Move SL to lock profit
"Close half" → Close 50% of position
"Take partial" → Close 10% at current level
"Runner active" → Switch to runner mode
```

---

## 8. LEARNING SYSTEM

**Read ALL messages to learn:**

```python
learning_categories = {
    "market_context": "Gold bullish due to rate cuts",
    "sentiment": "Risk-off environment",
    "technical_levels": "Support at 2675, resistance at 2700",
    "pattern_recognition": "Double bottom forming",
    "trader_confidence": "High confidence setup",
    "caution_flags": "Low volume, be careful",
    "expected_move": "Targeting 2750-2800"
}
```

**Store in:** `learning_database_lessons.jsonl`

**Use for:**
- Better signal timing
- Understanding context
- Adapting to market changes
- Improving entries

---

## 9. BUILD STEPS FOR HELIOS

### Step 1: Telegram Connection (Day 1)
- [ ] Get Telegram bot token from Caleb
- [ ] Connect to CallistoFX channel
- [ ] Read messages (signals + commentary)
- [ ] Store raw messages
- [ ] Test message parsing

### Step 2: Signal Parsing (Day 1)
- [ ] Parse symbol, direction, range, SL, TPs
- [ ] Handle different formats
- [ ] Validate signals
- [ ] Store structured signals

### Step 3: OANDA Integration (Day 2)
- [ ] Connect to OANDA API (creds in .env)
- [ ] Query live pip values
- [ ] Calculate position sizes
- [ ] Test order creation

### Step 4: 3-Tier Entry (Day 2)
- [ ] Split position into 3 orders
- [ ] Place at high/mid/low of range
- [ ] Set initial SL
- [ ] Monitor fills

### Step 5: Trade Management (Day 3)
- [ ] Monitor open positions
- [ ] Move SL to BE at +20
- [ ] Close partial at TPs (10% each)
- [ ] Activate runner at +100

### Step 6: Runner Strategy (Day 3)
- [ ] Trail SL (100 pips behind)
- [ ] Close 10% of remaining every +50 pips
- [ ] Continue until SL hit
- [ ] Log all actions

### Step 7: Learning System (Day 4)
- [ ] Parse commentary messages
- [ ] Extract patterns
- [ ] Store in database
- [ ] Use for context

### Step 8: Dashboard Integration (Day 4)
- [ ] Report trades to data.json
- [ ] Update P&L
- [ ] Show open positions
- [ ] Alert on important events

### Step 9: Deploy 24/7 (Day 5)
- [ ] Deploy on Render
- [ ] Set up health checks
- [ ] Configure auto-restart
- [ ] Test stability

### Step 10: Live Testing (Day 6-7)
- [ ] Paper trade for 2 days
- [ ] Verify all functions
- [ ] Check P&L tracking
- [ ] Fix any bugs

---

## 10. TECHNICAL REQUIREMENTS

**Runtime:** Python 3.10+
**Key Libraries:**
```
telethon (Telegram API)
requests (OANDA API)
redis (optional, for state)
asyncio (async operations)
```

**Environment Variables:**
```bash
OANDA_API_KEY=xxx
OANDA_ACCOUNT_ID=001-003-8520002-001
TELEGRAM_API_ID=xxx
TELEGRAM_API_HASH=xxx
TELEGRAM_BOT_TOKEN=xxx (NEED FROM CALEB)
```

**Files to Create:**
```
/agents/quanta/
├── telegram_monitor.py      # NEW - Your main file
├── oanda_client.py          # NEW - OANDA wrapper
├── position_calculator.py   # NEW - Size calculations
├── trade_manager.py         # NEW - Open trade management
├── runner_strategy.py       # NEW - Runner logic
├── signal_parser.py         # NEW - Parse CallistoFX
├── learning_engine.py       # NEW - Learn from commentary
├── reporting.py             # NEW - Dashboard reports
├── config.json              # Settings
└── logs/                    # Trade logs
```

---

## 11. WHAT I NEED FROM CALEB

1. **Telegram Bot Token** - To read CallistoFX channel
2. **CallistoFX Channel ID** - Which channel to monitor
3. **OANDA Practice Account** - For testing (already have live)
4. **Confirmation** - On strategy details above

---

## 12. KEY DIFFERENCES FROM OLD QUANTA

| Old Quanta | New Quanta (You Build) |
|------------|------------------------|
| Max trades limited | **NO LIMITS** |
| Just execute signals | **LEARN from commentary** |
| Fixed symbols | **ANY symbol** |
| Basic TP | **Multiple TPs + Runner** |
| Local only | **Render 24/7 deployment** |
| Single entry | **3-tier split entry** |
| Manual SL moves | **Auto SL management** |

---

**Helios - This is your complete build spec. Start with Step 1. Any questions?**
