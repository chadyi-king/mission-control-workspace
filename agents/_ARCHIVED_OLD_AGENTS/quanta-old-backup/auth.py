#!/usr/bin/env python3
"""One-time auth for Quanta"""
import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER
from telethon import TelegramClient

SESSION = BASE_DIR / 'sessions' / 'quanta'

async def main():
    print("Quanta Authentication")
    print("=" * 40)
    print(f"Phone: {PHONE_NUMBER}")
    print("")
    
    client = TelegramClient(str(SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=lambda: PHONE_NUMBER)
    
    me = await client.get_me()
    print(f"\n✓ Success! Logged in as: {me.first_name}")
    print("\nYou can now run: python3 quanta.py")
    
    await client.disconnect()

asyncio.run(main())