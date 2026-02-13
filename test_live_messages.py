#!/usr/bin/env python3
"""Test LIVE message reception from CallistoFX"""
from telethon import TelegramClient, events
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER

SESSION_FILE = '/tmp/quanta_telegram_session'

async def test_live():
    print("🧪 Testing LIVE message reception...")
    print(f"Start time: {datetime.now()}")
    print()
    
    client = TelegramClient(SESSION_FILE, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Not authorized")
        return False
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    # Find channel
    channel_id = None
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if "callistofx" in name.lower() and "premium" in name.lower():
            channel_id = dialog.id
            print(f"✅ Found channel: {name}")
            break
    
    if not channel_id:
        print("❌ Channel not found")
        return False
    
    # Get recent messages to verify connection
    print("\n📜 Recent messages (last 3):")
    async for message in client.iter_messages(channel_id, limit=3):
        print(f"   [{message.date}] {message.text[:60]}...")
    
    # Set up live handler
    print("\n🎯 Setting up LIVE handler...")
    messages_received = []
    
    @client.on(events.NewMessage(chats=channel_id))
    async def handler(event):
        text = event.message.text
        if text:
            print(f"\n🚨 LIVE MESSAGE: {datetime.now()}")
            print(f"   {text[:100]}...")
            messages_received.append(1)
    
    print("⏳ Listening for 60 seconds...")
    print("   Send a message to CallistoFX Premium to test")
    
    await asyncio.sleep(60)
    
    print(f"\n✅ Test complete. Messages received: {len(messages_received)}")
    
    if len(messages_received) == 0:
        print("\n⚠️ No messages received in 60 seconds.")
        print("   Possible causes:")
        print("   - No messages sent during test period")
        print("   - Event handler not working")
        print("   - Channel ID mismatch")
    
    await client.disconnect()
    return len(messages_received) > 0

if __name__ == '__main__':
    result = asyncio.run(test_live())
    sys.exit(0 if result else 1)
