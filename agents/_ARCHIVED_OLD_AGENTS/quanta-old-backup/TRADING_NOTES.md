# Trading Automation Notes (Quanta)

_Last updated: 2026-02-09_

## Signal Format
- Messages arrive as structured text:
  - `🟢PAIR🟢` (buy) or `🔴SELL🔴` (sell)
  - `RANGE: entryMin-entryMax`
  - `SL stopLoss`
  - `TP : tp1/tp2/tp3/tp4[/tp5]`
- Noise (chatter, comments) must be ignored unless it matches this structure.

## Entry & Positioning
- Use split entries when price dips through the range (e.g., 3 partial fills sized 0.33/0.33/0.34 of target risk).
- Breakeven is the weighted average of all filled entries.
- Order should execute only if live bid/ask falls inside the stated range (spread filter still TODO).

## Take-Profit Ladder & Trailing
- Close 10% of the position at each pip milestone: +20, +40, +60, +80, +100.
- On the first +20 pip move, move stop-loss to breakeven (weighted entry) so trade becomes risk-free.
- Continue trailing remainder with adjustable buffer (default 20 pips).
- When price reaches +200 pips, lift trailing stop so floor is +100 pips above weighted entry, then continue trailing.
- If signal says “let it ride”, skip fixed TP ladder and trail remainder only.

## Risk Controls (to implement)
- Default risk target: 1–2% of account balance per signal (auto-calc lot size from SL distance).
- Provide option for fixed lot size as fallback.
- Allow optional internal stop tighter than provider SL when their SL is too wide.

## Outstanding Work (requires Kimi 2.5)
1. Code real-time Telegram monitor + OANDA execution with above rules.
2. Add spread filter (skip if spread > configurable threshold).
3. Implement detection of “split the entry” instructions vs single entry.
4. Support manual overrides (e.g., “let it ride”, different trail distances).
5. Simulation/backtest harness using stored signal samples before going live.
