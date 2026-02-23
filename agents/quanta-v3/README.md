# QUANTA v3 (Personal Telegram -> OANDA Auto Execution)

## What this build does
- Uses **Telethon personal account** session (not Bot API).
- Resolves `🚀 CallistoFx Premium Channel 🚀` once and persists `channel_id` in `telegram_state.json`.
- Uses event handler: `@client.on(events.NewMessage(chats=channel_id))`.
- Persists `last_processed_message_id` and updates it **only after publish to the Redis signal stream**.
- Parses XAUUSD BUY/SELL range signals with tolerance for emoji/newlines/extra spaces.
- Publishes parsed signals to Redis stream `quanta.signals` for the executor to consume.
- Executes 3-tier LIMIT orders (33/33/34) with common SL (executor path).
- Runs TP ladder (from signal TP levels if provided, otherwise +20/+40/+60/+80/+100), breakeven move at first TP, and runner logic beyond the final TP with trailing SL.
- Persists active trade states in Redis (`quanta.open_trades`) when available and falls back to `open_trades.json`.
- Logs all errors to `logs/quanta.log`.
- Includes supervisor auto-restart loop.

## Required environment variables
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- `TELEGRAM_STRING_SESSION` (optional, recommended for lock-free Telegram auth)
- `OANDA_ACCOUNT_ID`
- `OANDA_API_KEY`
- `OANDA_ENVIRONMENT` = `LIVE` or `PRACTICE`
- `DRY_RUN` = `1` (default) or `0` to allow live orders
- `REDIS_URL` (default `redis://localhost:6379/0`)

### Redis fallback behavior
- Preferred: run a real Redis server for durable cross-process streams.
- If Redis is unavailable, QUANTA v3 automatically falls back to an in-process Redis-compatible backend (`fakeredis`).
- Fallback mode is suitable for local testing, especially with `--role all` in a single process.

### Telegram session lock avoidance
- If you see `sqlite3.OperationalError: database is locked`, use `TELEGRAM_STRING_SESSION`.
- String sessions bypass the local `.session` sqlite file, so file-lock conflicts are avoided.
- You can generate a value once using:
	- `python create_string_session.py`
	- then set `TELEGRAM_STRING_SESSION=...` in `.env`

## Run
```bash
pip install -r requirements.txt
python main.py --role all
```

Or run components separately:
```bash
python main.py --role listener
python main.py --role manager
python main.py --role executor
```
