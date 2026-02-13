#!/usr/bin/env python3
import asyncio
import sys
import json
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER
from telethon import TelegramClient

CODE = sys.argv[1] if len(sys.argv) > 1 else None

async def main():
    if not CODE:
        print("Usage: python3 quick_auth.py <code>")
        return
    
    client = TelegramClient('/tmp/quanta_telegram_session', int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    await client.connect()
    
    # Request code first to get hash
    result = await client.send_code_request(PHONE_NUMBER)
    
    # Use code immediately
    try:
        await client.sign_in(PHONE_NUMBER, CODE, phone_code_hash=result.phone_code_hash)
        print("✅ AUTHENTICATED!")
        me = await client.get_me()
        print(f"   User: {me.first_name}")
        await client.disconnect()
        print("\n✅ Quanta session ready!")
    except Exception as e:
        print(f"❌ {e}")
        await client.disconnect()

asyncio.run(main())
