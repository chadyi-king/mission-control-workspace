#!/usr/bin/env python3
"""Test Telegram connection and message reception"""
from telethon import TelegramClient, events
import asyncio
import sys

# Load config
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_test_session'

async def test_connection():
    print("🧪 Testing Telegram Connection...")
    print(f"API ID: {TELEGRAM_API_ID}")
    print(f"Phone: {PHONE_NUMBER}")
    print()
    
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    
    try:
        print("⏳ Connecting to Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ NOT AUTHORIZED - Need to login")
            print("Sending code request...")
            await client.send_code_request(PHONE_NUMBER)
            print("📱 Check your phone for Telegram code")
            return False
        
        print("✅ Connected and authorized!")
        me = await client.get_me()
        print(f"   Logged in as: {me.first_name} (@{me.username})")
        print()
        
        # Find CallistoFX channel
        print("🔍 Searching for CallistoFx Premium channel...")
        channel_found = False
        async for dialog in client.iter_dialogs():
            name = dialog.name or ""
            if "callistofx" in name.lower():
                print(f"   Found: {name} (ID: {dialog.id})")
                if "premium" in name.lower():
                    print(f"   ✅ This is the PREMIUM channel!")
                    channel_found = dialog.id
                    break
        
        if not channel_found:
            print("   ❌ CallistoFx Premium not found")
            return False
        
        print()
        print("🎯 Setting up message handler...")
        
        @client.on(events.NewMessage(chats=channel_found))
        async def handle_new_message(event):
            text = event.message.text
            if text:
                print(f"\n📨 NEW MESSAGE RECEIVED:")
                print(f"   Time: {event.message.date}")
                print(f"   Text: {text[:100]}...")
                print(f"   ✅ LIVE STREAM WORKING!")
        
        print("⏳ Listening for messages (30 seconds)...")
        print("   Send a test message to CallistoFx Premium channel")
        print()
        
        # Run for 30 seconds
        await asyncio.sleep(30)
        
        print("\n✅ Test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.disconnect()

if __name__ == '__main__':
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
