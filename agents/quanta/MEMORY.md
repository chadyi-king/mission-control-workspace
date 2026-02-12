# Quanta Memory
## Trading Strategy Parameters (Caleb's Rules)

### Position Sizing
```
Account Balance: $10,000
Risk per trade: 2% = $200

Formula: Lot Size = $200 ÷ (Entry - SL in pips)

Example: XAUUSD BUY 2680-2685, SL 2665
- Entry: 2682.5 (middle of range)
- Risk: 2682.5 - 2665 = 17.5 pips
- Size: $200 ÷ 17.5 = 0.11 lots
```

### Exit Strategy (CALEB'S EXACT RULES)
```
Signal: XAUUSD BUY 2680-2685, SL 2665, TP 2700/2720/2740/2760/2780

Execute ONE position (not split):
- Buy 0.11 lots XAUUSD @ 2682.5
- SL: 2665

Exit Plan:
TP1 (+10%): 2700 → Close 10%, move SL to breakeven
TP2 (+10%): 2720 → Close 10%
TP3 (+20%): 2740 → Close 20%
TP4 (+30%): 2760 → Close 30%
TP5 (+30% runner): 2780 → Trail SL at -50 pips from current

After Trade Active:
- Price hits TP1 (+20 pips): Close 10%, move SL to breakeven
- Price hits +50 pips: Move SL to +20 pips (lock profit)
- Price hits +100 pips: Trail SL at -50 pips from current
```

### Hard Rules
- Max daily risk: 6% (3 trades max)
- Max concurrent trades: 2
- Max trades per day: 5
- Signal score must be ≥ 40
- Always use stop loss
- Always move to breakeven at TP1

### OANDA Setup
- Practice account for testing
- Live account when ready
- API credentials needed
