#!/bin/bash
# One-time re-auth script for Quanta

echo "=========================================="
echo "Quanta Telegram Re-Authentication"
echo "=========================================="
echo ""
echo "This will authenticate Quanta with Telegram."
echo "You'll receive an SMS code on your phone."
echo ""

cd ~/.openclaw/workspace/agents/quanta

# Clear expired sessions
rm -f /tmp/quanta_telegram_session.session
rm -f quanta_session.session

# Run interactive auth
python3 -c "
from telethon import TelegramClient
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

client = TelegramClient('/tmp/quanta_telegram_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)

async def main():
    await client.start(phone=lambda: PHONE_NUMBER)
    print('✅ Authentication successful!')
    me = await client.get_me()
    print(f'Logged in as: {me.first_name} ({me.phone})')
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
"

echo ""
echo "=========================================="
echo "Auth complete. You can now restart Quanta:"
echo "  ./runner.sh"
echo "=========================================="