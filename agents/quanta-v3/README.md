# QUANTA v3

Rebuilt Telegram->OANDA auto-trading runtime with polling monitor, fuzzy parser, risk engine, and Redis trade state.

## Modified core modules
- `telegram_monitor.py`
- `signal_parser.py`
- `risk_manager.py`
- `trade_manager.py`
- `position_manager.py`

## Telegram monitoring logic
- Personal Telethon session login.
- Resolve and persist channel id in `telegram_state.json`.
- On startup pull last 50 messages to `deque(maxlen=50)`.
- Poll every 3 seconds with `iter_messages(channel_id, min_id=last_processed_id)`.
- Persist `last_processed_id` to disk after each processed message.
- Never reprocess old message ids or duplicate `signal_id`.

## Execution strategy
- 3-tier LIMIT entries:
  - BUY: low / mid / high
  - SELL: high / mid / low
  - allocation: 33% / 33% / 34%
- Shared SL for all tiers.
- TP ladder from first entry using channel-pip distance.
- +20/+40/+60/+80/+100 close 10% of original size.
- +20 moves all SL to breakeven.
- Runner at +100, then every +100 closes 10% of remaining size and updates trailing SL 100 channel pips behind.

## Risk model
- First 10 trades: $30 total risk ($10-equivalent per tier split).
- After 10 trades: 2% account balance total risk split across 3 tiers.
- Units derived from OANDA instrument metadata and SL distance; abort on expected-loss breach.

## Redis keys
- `quanta.processed_signals`
- `quanta.telegram.state`
- `quanta.active_signals`
- `quanta.signal:<signal_id>`

## Run
```bash
pip install -r requirements.txt
python main.py --role all
```


## Price-distance risk model (new)
- Position sizing ignores broker pip values for risk calculations.
- Core formula: `risk_in_price = abs(entry_price - stop_loss_price)`.
- Universal sizing: `lot_size = account_risk_usd / (risk_in_price * contract_size)` then `units = lot_size * contract_size`.
- UI/explain payload now includes:
  - `channel_pip_distance`
  - `broker_pip_distance`
  - `actual_price_distance`
  - `total_usd_risk`
- Engine always executes by **actual market price distance** first.


## Channel pip conversion (execution triggers)
- TP/BE/Runner triggers use channel-pip conversion into price distance.
- `XAUUSD`: 1 channel pip = 0.1 price.
- Example: TP1 (20 channel pips) = `2.0` price distance.
- Engine trigger logic is price-distance based (`channel_pips_to_price`) and no longer uses fixed pip multipliers.


## OANDA unit risk conversion
- Sizing now converts stop distance into USD loss per unit using broker pip size + pip value.
- Core conversion uses `get_usd_loss_per_unit(symbol, entry, stop)` in `oanda_client.py`.
- Tier units are computed as `risk_per_tier / usd_loss_per_unit` to keep realized SL loss aligned with USD risk targets.
