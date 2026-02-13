#!/usr/bin/env python3
"""Request new Telegram code"""
from telethon import TelegramClient
import asyncio
import sys

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'

async def main():
    print("📱 Requesting new Telegram code...")
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    await client.connect()
    
    if await client.is_user_authorized():
        print("✅ Already authorized!")
        me = await client.get_me()
        print(f"   User: {me.first_name}")
        await client.disconnect()
        return True
    
    print("⏳ Sending code request...")
    await client.send_code_request(PHONE_NUMBER)
    print("✅ Code sent! Check your phone.")
    print("   Then run: python3 enter_code.py <code>")
    
    await client.disconnect()
    return True

asyncio.run(main())
