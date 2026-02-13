#!/usr/bin/env python3
"""Complete Telegram authentication with code"""
from telethon import TelegramClient
import asyncio
import sys

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'
CODE = "86683"

async def authenticate():
    print("🔐 Completing Telegram authentication...")
    
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    try:
        await client.connect()
        
        if await client.is_user_authorized():
            print("✅ Already authorized!")
            return True
        
        print(f"⏳ Signing in with code: {CODE}")
        await client.sign_in(PHONE_NUMBER, CODE)
        
        print("✅ Authentication successful!")
        me = await client.get_me()
        print(f"   Logged in as: {me.first_name}")
        
        # Test by listing dialogs
        print("\n📋 Testing - listing channels...")
        async for dialog in client.iter_dialogs(limit=10):
            if "callistofx" in (dialog.name or "").lower():
                print(f"   ✅ Found: {dialog.name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == '__main__':
    result = asyncio.run(authenticate())
    sys.exit(0 if result else 1)
