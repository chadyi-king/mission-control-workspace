# QUANTA TRADING PARAMETERS (CORRECTED)
## From Caleb's Message 2026-02-13 01:00

---

## 1. PROTECT YOUR MONEY (STOP LOSS RULES)

**Initial:** Use signal's SL

**At +20 pips profit:** Move SL to entry (breakeven - can't lose)

**At +50 pips:** Trail SL 30 pips behind current price

**Risk Limit:** Never more than 2% per trade

---

## 2. TAKE PROFITS (DEPENDS ON TREND STRENGTH)

### Strong Trend:
| Level | Close | Pips |
|-------|-------|------|
| TP1 | 10% | +20 |
| TP2 | 10% | +50 |
| TP3 | 30% | +100 |
| Runner | 50% | Let it run |

### Weak Trend:
| Level | Close | Pips |
|-------|-------|------|
| TP1 | 20% | +20 |
| TP2 | 30% | +40 |
| TP3 | 50% | +60 |

---

## 3. RUNNER POSITION (BIG MONEY)

**What it is:** The 40-50% you don't sell early

**Management:**
- At +50 pips: Protect with SL at entry (locked)
- At +100 pips: Lock in +50 pips minimum
- Let it run to +200 or more if trend continues

---

## 4. QUALITY CHECK

- **Good setup** = Full size (100%)
- **Okay setup** = Half size (50%)
- **Bad setup** = Skip trade

---

## 5. EXAMPLE TRADE

**Signal:** XAUUSD BUY  
**Entry:** 2680.50  
**SL:** 2675.50 (50 pips / $50 per lot)  
**Trend:** Strong (London session)  
**Account:** $10,000

**Position Sizing:**
- Risk: 2% of $10,000 = $200
- SL distance: 50 pips = $50 per lot
- Position: $200 ÷ $50 = **0.4 lots**

**Trade Execution:**

| Stage | Action | Pips | Profit (0.4 lot) |
|-------|--------|------|------------------|
| Entry | Buy 0.4 lots @ 2680.50 | - | - |
| +20 pips (2682.50) | Close 10% (0.04 lot) | +20 | +$8 |
| Move SL | SL to 2680.50 (breakeven) | - | - |
| +50 pips (2685.50) | Close 10% (0.04 lot) | +50 | +$20 |
| Trail SL | SL trails 30 pips behind | - | - |
| +100 pips (2690.50) | Close 30% (0.12 lot) | +100 | +$120 |
| Runner | 50% (0.20 lot) running | Variable | Variable |

**Key Differences from Old Code:**
1. SL moves to BE at +20 pips (not at TP1)
2. Trail starts at +50 pips (30 pips behind)
3. Exit splits depend on trend strength
4. Runner is 50% (not 30%)

---

## IMPLEMENTATION CHANGES NEEDED

1. **Signal Scoring** → Determine strong/weak trend
2. **SL Management** → Move to BE at +20, trail at +50
3. **Exit Splits** → Strong (10/10/30/50) vs Weak (20/30/50)
4. **Position Sizing** → Still 2% of balance
5. **Runner Management** → 50% position, trail SL

---

*This is the CORRECT version. Update Quanta code.*
