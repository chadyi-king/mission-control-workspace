# QUANTA AGENT - SIMPLE SETUP BOARD

## CHECK WHAT YOU HAVE

**Run this in Command Prompt:**
```cmd
ollama list
```

**Tell me what models show up.**

---

## MODELS NEEDED

| Model | Purpose | Size | Command |
|-------|---------|------|---------|
| **llava:13b** | Eyes - reads screenshots | 8GB | `ollama pull llava:13b` |
| **codellama:7b** | Brain - trading logic | 4GB | `ollama pull codellama:7b` |

**If not installed, run those commands.**

---

## SIMPLIFIED PARAMETERS

### Account
- **Balance:** $2,000
- **Risk per trade:** $40 (2%)
- **Risk auto-adjusts:** If balance grows to $4,000 → risk becomes $80

### Signal Detection
- **Watch:** CallistoFx Premium Channel
- **Look for:** "XAUUSD BUY" or "XAUUSD SELL"
- **Screenshot every:** 2 seconds
- **Parse:** Entry range, SL, 5x TP

### Entry Strategy (Split Risk)
```
Signal: Buy Range 2685-2675

Entry 1: 2685 @ 33% size (if price drops, this hits SL first)
Entry 2: 2680 @ 33% size (middle, balanced)
Entry 3: 2675 @ 34% size (best price, safest)

Total: 0.04 lots, $40 risk
```

### Exit Strategy
```
TP1 (+20 pips): Close Entry 1, move others to breakeven
TP2 (+50 pips): Close 20%, trail SL
TP3 (+100 pips): Close 20%, lock profit
TP4 (+150 pips): Close 30%
TP5 (+200 pips): Runner with trailing SL
```

---

## HOW QUANTA LEARNS (Simple)

### Pattern Storage
```python
# After each trade:
IF trade_profitable:
    SAVE: "This setup worked"
    Examples: Time of day, pattern type, market condition

IF trade_lost:
    SAVE: "Avoid this setup"
    Examples: Wrong session, choppy market, bad entry
```

### What She Learns
1. **Timing:** "XAUUSD signals work best at 8AM and 1PM"
2. **Patterns:** "Inside bar sweeps win 78% of time"
3. **Risk:** "If SL >30 pips, reduce size"
4. **Market:** "Don't trade during news events"

### Learning Loop
```
Trade 1 → Result: +45 pips → Store: "Worked well"
Trade 2 → Result: -20 pips → Store: "Wrong timing"
Trade 3 → Result: +60 pips → Store: "Strong trend helps"
...
Trade 50 → Pattern database full → Better decisions
```

---

## WORKFLOW (Step by Step)

```
1. START
   ↓
2. Screenshot every 2 seconds
   ↓
3. LLaVA reads: "What text is here?"
   ↓
4. IF signal detected:
   ↓
5. CodeLlama thinks:
   - "Calculate entries"
   - "Check risk"
   - "Create plan"
   ↓
6. SHOW YOU: Trading plan
   ↓
7. YOU SAY: YES / NO / MODIFY
   ↓
8. IF YES: Execute on OANDA
   ↓
9. Monitor trade
   ↓
10. At TP1: Move to breakeven
    ↓
11. Report result
    ↓
12. Store in memory
    ↓
13. REPEAT
```

---

## TESTING PHASES

| Phase | Trades | Size | Approval |
|-------|--------|------|----------|
| Paper | 20 | $0 (fake) | Every trade |
| Mini | 20 | $2-5 | Every trade |
| Small | 10 | $10-20 | Every 3rd trade |
| Full | ∞ | $40 (2%) | Daily only |

**Only proceed after passing each phase.**

---

## WHAT YOU NEED TO INSTALL

If not already done:
```cmd
ollama pull llava:13b
ollama pull codellama:7b
```

Then I create the agent file.

**What does `ollama list` show you?**
