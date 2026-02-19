# QUANTA v3 (Personal Telegram -> OANDA Auto Execution)

## What this build does
- Uses **Telethon personal account** session (not Bot API).
- Resolves `🚀 CallistoFx Premium Channel 🚀` once and persists `channel_id` in `telegram_state.json`.
- Uses event handler: `@client.on(events.NewMessage(chats=channel_id))`.
- Persists `last_processed_message_id` and updates it **only after parse + trade execution succeed**.
- Parses XAUUSD BUY/SELL range signals with tolerance for emoji/newlines/extra spaces.
- Executes 3-tier market orders (33/33/34) with common SL.
- Runs TP ladder (+20/+40/+60/+80/+100), breakeven move at +20, and runner logic beyond +100 with trailing SL.
- Persists active trade states in `open_trades.json` and resumes on restart.
- Logs all errors to `logs/quanta.log`.
- Includes supervisor auto-restart loop.

## Required environment variables
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- `OANDA_ACCOUNT_ID`
- `OANDA_API_KEY`
- `OANDA_ENVIRONMENT` = `LIVE` or `PRACTICE`

## Run
```bash
pip install -r requirements.txt
python main.py --role all
```

Or run components separately:
```bash
python main.py --role listener
python main.py --role manager
```
