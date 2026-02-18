# Quanta Trading Bot - Key Context

## Primary Focus
**CallistoFX Trading Only**

## Channel to Monitor
**🚀 CallistoFx Premium Channel 🚀**

This is the ONLY Telegram channel Quanta should monitor for signals.

---

## Strategy Summary

### Entry: 3-Tier Split
| Tier | % of Position | Entry Point |
|------|---------------|-------------|
| Tier 1 | 33% | High of signal range |
| Tier 2 | 33% | Mid of signal range |
| Tier 3 | 34% | Low of signal range |

### Phase 1: 5 Fixed TPs (First 50% of Position)
**Close 10% of ORIGINAL position at each level:**

| TP | Pips | Action | Cumulative Closed |
|----|------|--------|-------------------|
| TP1 | +20 | Close 10%, move SL to BE | 10% |
| TP2 | +40 | Close 10% | 20% |
| TP3 | +60 | Close 10% | 30% |
| TP4 | +80 | Close 10% | 40% |
| TP5 | +100 | Close 10%, **ACTIVATE RUNNER** | 50% |

### Phase 2: Runner Strategy (Remaining 50%)
**Activation:** At +100 pips (TP5)

**Rule:** Every +50 pips beyond +100, close **10% of REMAINING** position + trail SL

**Example (starting with 100 units):**
```
After 5 TPs: 50 units remain (runner)

+150 pips: Close 10% of 50 = 5 units → 45 remain, SL at +50
+200 pips: Close 10% of 45 = 4.5 units → 40.5 remain, SL at +100
+250 pips: Close 10% of 40.5 = 4.05 units → 36.45 remain, SL at +150
+300 pips: Close 10% of 36.45 = 3.645 units → 32.8 remain, SL at +200
... continues until SL hit
```

**Trailing SL:** 100 pips behind current price (runner only)

---

## Position Sizing

### Formula
```
Units = Risk Amount ÷ (Pip Value × SL Distance)
```

### Example (XAUUSD)
- Risk: SGD $20
- SL Distance: 7.5 pips
- Pip Value: ~$1.19 per 100 units
- Calculation: $20 ÷ ($0.0119 × 7.5) = **224 units**

### Steps
1. Query OANDA pricing API for live pip value
2. Calculate units based on $20-50 risk and SL distance
3. Verify margin requirement before placing order

---

## Risk Management
- **Max risk per trade:** $20-50 SGD
- **No daily trade limits** (Caleb removed this constraint)
- **No concurrent trade limits** (Caleb removed this constraint)
- **Paper trading first**, then live

---

## Credentials
- **OANDA Account:** 001-003-8520002-001
- **Environment:** Practice (paper trading)
- **API Token:** See `agents/quanta/.env`
- **Telegram:** Need bot token from Caleb to access CallistoFX Premium

---

## Learning System
Quanta should:
- Store trader patterns from CallistoFX commentary
- Learn when signals typically come
- Understand "strong trend" vs "weak trend" context
- Adapt to trader style changes
- Not just execute signals blindly

---

## Key Files
- `QUANTA_BUILD_PLAN_FOR_HELIOS.md` - Full 367-line build specification
- `QUANTA_TRADING_STRATEGY_FINAL.md` - Previous strategy documentation
- `monitor_callistofx.py` - Previous working code reference
- `.env` - OANDA credentials
