#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER
from telethon import TelegramClient

async def main():
    client = TelegramClient('/tmp/quanta_final_session', int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    await client.connect()
    
    print("📱 Requesting code...")
    result = await client.send_code_request(PHONE_NUMBER)
    
    print("⏳ Type the code from your phone and press Enter:")
    code = input("> ").strip()
    
    print(f"🔐 Using code: {code}")
    try:
        await client.sign_in(PHONE_NUMBER, code, phone_code_hash=result.phone_code_hash)
        print("✅ AUTHENTICATED SUCCESSFULLY!")
        
        me = await client.get_me()
        print(f"   User: {me.first_name}")
        
        # Find CallistoFX
        print("\n📋 Channels:")
        async for dialog in client.iter_dialogs():
            if "callistofx" in (dialog.name or "").lower():
                print(f"   ✅ {dialog.name}")
        
        await client.disconnect()
        print("\n✅ Session saved! Quanta is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await client.disconnect()
        return False

asyncio.run(main())
