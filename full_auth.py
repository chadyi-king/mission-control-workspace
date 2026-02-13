#!/usr/bin/env python3
"""Full authentication flow"""
from telethon import TelegramClient
import asyncio
import sys

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'
CODE = "11868"

async def main():
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    print("🔐 Connecting to Telegram...")
    await client.connect()
    
    if await client.is_user_authorized():
        print("✅ Already authorized!")
        me = await client.get_me()
        print(f"   User: {me.first_name}")
    else:
        print("⏳ Requesting code...")
        result = await client.send_code_request(PHONE_NUMBER)
        phone_code_hash = result.phone_code_hash
        
        print(f"📱 Using code: {CODE}")
        try:
            await client.sign_in(PHONE_NUMBER, CODE, phone_code_hash=phone_code_hash)
            print("✅ AUTHENTICATED!")
            me = await client.get_me()
            print(f"   User: {me.first_name}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Code may have expired. Need new code.")
            await client.disconnect()
            return False
    
    # Test: List channels
    print("\n📋 Channels found:")
    callistofx_id = None
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if "callistofx" in name.lower():
            print(f"   ✅ {name} (ID: {dialog.id})")
            if "premium" in name.lower():
                callistofx_id = dialog.id
    
    await client.disconnect()
    
    if callistofx_id:
        print(f"\n✅ Ready! CallistoFX Premium ID: {callistofx_id}")
        return True
    else:
        print("\n⚠️ CallistoFX Premium not found")
        return False

asyncio.run(main())
