#!/usr/bin/env python3
"""
Quanta Telegram Authentication Script
Run this ONCE on your main computer to create session file
"""

import asyncio
import os
import sys

# Your credentials (already filled in)
API_ID = '32485688'
API_HASH = 'f9ee9ff7b3b7c37bb3b213709eb3ad99'
PHONE_NUMBER = '+6591593838'
SESSION_FILE = 'quanta_session'

async def main():
    print("=" * 60)
    print("QUANTA TELEGRAM AUTHENTICATION")
    print("=" * 60)
    print()
    print("This will create a session file for 24/7 monitoring.")
    print("Run this ONCE on your main computer.")
    print()
    
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
    except ImportError:
        print("Installing required package...")
        os.system(f"{sys.executable} -m pip install telethon -q")
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
    
    # Create client
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    print("Connecting to Telegram...")
    await client.connect()
    
    if await client.is_user_authorized():
        print("✅ Already authenticated!")
    else:
        print(f"Sending code to {PHONE_NUMBER}...")
        await client.send_code_request(PHONE_NUMBER)
        
        code = input("\nEnter the SMS code you received: ")
        
        try:
            await client.sign_in(PHONE_NUMBER, code)
            print("✅ Authentication successful!")
        except SessionPasswordNeededError:
            password = input("Two-factor password: ")
            await client.sign_in(password=password)
            print("✅ Authentication successful!")
    
    # Verify we can see the channel
    print("\nChecking for CallistoFX channel...")
    channel_found = False
    
    async for dialog in client.iter_dialogs():
        if '🚀 CallistoFx Premium Channel 🚀' in dialog.title:
            print(f"✅ Found channel: {dialog.title}")
            channel_found = True
            break
    
    if not channel_found:
        print("⚠️  Channel not found. Make sure you're subscribed.")
    
    await client.disconnect()
    
    print()
    print("=" * 60)
    print("AUTHENTICATION COMPLETE!")
    print("=" * 60)
    print()
    print(f"Session file created: {SESSION_FILE}.session")
    print()
    print("NEXT STEPS:")
    print("1. Send this file to Helios:")
    print(f"   {SESSION_FILE}.session")
    print()
    print("2. Helios will deploy Quanta to Render with this session")
    print()
    print("3. Quanta will monitor 24/7 using your session")
    print()
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
