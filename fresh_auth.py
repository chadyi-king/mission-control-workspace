#!/usr/bin/env python3
"""Fresh authentication with code"""
from telethon import TelegramClient
import asyncio
import sys

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'
CODE = "86683"

async def main():
    print("🔐 Fresh Telegram authentication...")
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    await client.connect()
    
    print("⏳ Signing in...")
    try:
        await client.sign_in(PHONE_NUMBER, CODE)
        print("✅ AUTHENTICATED SUCCESSFULLY!")
        
        me = await client.get_me()
        print(f"   User: {me.first_name} (@{me.username})")
        
        # Test: List channels
        print("\n📋 Channels:")
        async for dialog in client.iter_dialogs(limit=20):
            if "callistofx" in (dialog.name or "").lower():
                print(f"   ✅ {dialog.name} (ID: {dialog.id})")
        
        await client.disconnect()
        print("\n✅ Session saved. Ready for Quanta.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await client.disconnect()
        return False

asyncio.run(main())
