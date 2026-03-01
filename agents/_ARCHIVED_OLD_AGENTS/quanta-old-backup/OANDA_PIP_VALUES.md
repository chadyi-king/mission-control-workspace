# OANDA_PIP_VALUES.md
## CRITICAL: Check Pip Value Before EVERY Trade

## The Rule
**NEVER assume pip value. Check OANDA display first.**

Each instrument has different pip value:
- XAUUSD (Gold): ~$1.19 SGD per pip (varies with price)
- EURUSD: ~$0.01 per unit per pip
- GBPUSD: Different from EURUSD
- BTCUSD: Completely different
- US30, US100: Different again

## How to Check (OANDA App)
1. Open "New Trade" screen
2. Select instrument
3. Look for: "1 PIP = $X.XX"
4. Use THIS value for calculations

## Position Size Formula
```
Correct Formula:
Units = Risk Amount ÷ (Pip Value × SL Distance in Pips)

Example (XAUUSD):
- Risk: $20
- Pip Value: $1.19 SGD (~$0.88 USD)
- SL Distance: 10 pips
- Units = $20 ÷ ($0.88 × 10) = $20 ÷ $8.80 = 2.27 units

NOT 94 units!
```

## Common Mistakes
❌ Assume all pairs = $0.01 per unit
❌ Use same calculation for gold as forex
❌ Don't check OANDA's displayed pip value
❌ Calculate based on other brokers' values

## Pre-Trade Checklist
- [ ] Check OANDA's "1 PIP = $X" display
- [ ] Calculate: Risk ÷ (Pip Value × SL Distance)
- [ ] Verify units match calculation
- [ ] Double-check SL distance
- [ ] Confirm total risk = intended amount

## Instrument-Specific Notes

### XAUUSD (Gold)
- Pip value changes with gold price
- Currently: ~$1.19 SGD per pip at current price
- 1 unit ≠ $0.01
- Much higher pip value than forex pairs

### Forex Pairs (EURUSD, GBPUSD, etc.)
- Usually closer to $0.01 per unit per pip
- But CHECK - not always exact

### Indices (US30, US100)
- Completely different calculation
- Check OANDA display

### Crypto (BTCUSD)
- Volatile pip values
- Always verify before trading

## Emergency Stop
**If calculation doesn't match OANDA display:**
1. DO NOT TRADE
2. Recalculate using correct pip value
3. Get confirmation before executing

## Remember
**One wrong pip value assumption = $1,000+ loss potential**

Always. Check. First.
