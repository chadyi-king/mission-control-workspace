#!/usr/bin/env python3
"""Complete authentication with code"""
from telethon import TelegramClient
import asyncio
import sys

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'
CODE = "11868"

async def main():
    print("🔐 Completing authentication...")
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    await client.connect()
    
    print(f"⏳ Using code: {CODE}")
    try:
        await client.sign_in(PHONE_NUMBER, CODE)
        print("✅ AUTHENTICATED!")
        
        me = await client.get_me()
        print(f"   User: {me.first_name} (@{me.username})")
        
        # Find CallistoFX
        print("\n📋 Finding channel...")
        async for dialog in client.iter_dialogs():
            if "callistofx" in (dialog.name or "").lower():
                print(f"   ✅ {dialog.name}")
        
        await client.disconnect()
        print("\n✅ Session saved!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await client.disconnect()
        return False

asyncio.run(main())
