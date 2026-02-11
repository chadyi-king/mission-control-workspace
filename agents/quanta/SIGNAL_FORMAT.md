# Signal Parser Configuration

## Signal Format Detected

### Example Signal:
```
🟢XAUUSD🟢
BUY
RANGE: 5010-5016.5
SL 4995
TP : 5030/5040/5060/5100
```

### Color Codes:
- 🟢 = BUY (Long)
- 🔴 = SELL (Short)

### Parsed Fields:
| Field | Example | Meaning |
|-------|---------|---------|
| Pair | XAUUSD | Gold/USD |
| Direction | BUY | Long position |
| Entry Range | 5010-5016.5 | Buy anywhere in this range |
| Stop Loss | 4995 | Fixed SL price |
| Take Profits | 5030/5040/5060/5100 | 4 TP levels |

---

## Trading Logic

### Entry Strategy:
- **Type:** Range entry (not single price)
- **Action:** Market buy if price within 5010-5016.5
- **Timeframe:** Execute immediately on signal

### Stop Loss:
- **Type:** Fixed price
- **Position:** Below entry for BUY, above for SELL
- **No trailing** (fixed at 4995)

### Take Profit Strategy (TRAILING):
User wants **trailing TP**, not fixed levels.

**Proposed Logic:**
```
TP1 (5030): Close 25% position
TP2 (5040): Close 25% position, move SL to breakeven
TP3 (5060): Close 25% position, activate trailing
TP4 (5100): Close final 25% or trail with 20-pip buffer
```

**Trailing Rules:**
- After TP3 (5060), activate trailing stop
- Trail distance: 20 pips (or 0.5% of price)
- If price reverses 20 pips from high, close remaining

---

## Risk Management (No Lot Size Provided)

Since signals don't include lot size:

### Option 1: Fixed Risk %
- Risk 2% of account per trade
- Calculate lot size based on SL distance

### Option 2: Fixed Lot Size
- User sets default (e.g., 0.1 lots for XAUUSD)
- Same size every trade

### Option 3: Volatility-Based
- Adjust lot size based on ATR (Average True Range)
- Bigger SL = smaller lot, smaller SL = bigger lot

**Recommended:** Option 1 (2% risk per trade)

---

## Signal Detection Patterns

### BUY Signal Pattern:
```
🟢{PAIR}🟢
BUY
RANGE: {MIN}-{MAX}
SL {STOP_PRICE}
TP : {TP1}/{TP2}/{TP3}/{TP4}
```

### SELL Signal Pattern:
```
🔴{PAIR}🔴
SELL
RANGE: {MIN}-{MAX}
SL {STOP_PRICE}
TP : {TP1}/{TP2}/{TP3}/{TP4}
```

### Regex Patterns:
- Pair: `[A-Z]{6}` or `XAUUSD|XAGUSD|US30|US100`
- Direction: `BUY|SELL`
- Range: `RANGE:\s*(\d+\.?\d*)-(\d+\.?\d*)`
- SL: `SL\s+(\d+\.?\d*)`
- TP: `TP\s*:\s*(\d+\.?\d*(?:/\d+\.?\d*)*)`

---

## Output Format for TradingView/OANDA

### TradingView Alert JSON:
```json
{
  "action": "buy",
  "symbol": "XAUUSD",
  "entry_range": [5010, 5016.5],
  "stop_loss": 4995,
  "take_profits": [5030, 5040, 5060, 5100],
  "trailing_enabled": true,
  "trailing_activation": 5060,
  "trailing_distance": 20,
  "risk_percent": 2
}
```

### OANDA Order:
```
Instrument: XAU_USD
Units: [Calculated based on 2% risk]
Type: MARKET
Stop Loss: 4995
Take Profits: Multiple (5030, 5040, 5060, 5100)
Trailing Stop: Activate at 5060, 20-pip trail
```

---

## Special Considerations for XAUUSD (Gold)

- **Pip value:** 1 pip = $0.01 for 1 unit
- **Spread:** Typically wider than forex pairs
- **Volatility:** High - fast moves
- **Session:** 24/5 but most active during London/NY overlap
- **Margin:** Check leverage (usually 20:1 or 50:1)

---

## Implementation Notes

1. **Speed is critical** - Execute within 10 seconds of signal
2. **Range validation** - Check current price is within range before entry
3. **Partial closes** - Need broker support for multiple TP levels
4. **Trailing stop** - Manual management if broker doesn't support
5. **Logs** - Record every signal, entry, exit for backtesting

---

## Next Steps

1. ✅ Signal format documented
2. ⏳ Write Python parser (quanta_signal_parser.py)
3. ⏳ Connect to Telegram (user session)
4. ⏳ Connect to OANDA API
5. ⏳ Test with paper trading
6. ⏳ Deploy and monitor