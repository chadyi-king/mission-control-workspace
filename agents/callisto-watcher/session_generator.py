#!/usr/bin/env python3
"""
Session Generator for CallistoFX Watcher
One-time setup to generate MTProto session string
"""

import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 2040  # Telethon default API ID
API_HASH = "b18441a1ff607e10a989891a5462e627"  # Telethon default API hash

print("=" * 60)
print("CallistoFX Watcher - Session Generator")
print("=" * 60)
print()
print("This will generate a session string for your Telegram account.")
print("You only need to do this ONCE.")
print()

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    
    session_string = client.session.save()
    
    print()
    print("=" * 60)
    print("SUCCESS! Your session string:")
    print("=" * 60)
    print()
    print(session_string)
    print()
    print("=" * 60)
    print()
    print("IMPORTANT:")
    print("1. Copy the session string above")
    print("2. Save it as TELEGRAM_SESSION environment variable")
    print("3. Or paste it into Render dashboard")
    print("4. NEVER share this string with anyone!")
    print()
    print("You can now deploy the watcher to Render.")
    
    # Also save to file
    with open("session.txt", "w") as f:
        f.write(session_string)
    print()
    print("Session also saved to: session.txt")
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
