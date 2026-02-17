#!/usr/bin/env python3
"""
Auth with code from file
"""

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER
from telethon import TelegramClient

SESSION = BASE_DIR / 'sessions' / 'quanta'
CODE_FILE = BASE_DIR / 'code.txt'

async def main():
    print("Quanta Authentication")
    print("=" * 40)
    print(f"Phone: {PHONE_NUMBER}")
    print()
    
    client = TelegramClient(str(SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.connect()
        
        if await client.is_user_authorized():
            print("Already authorized!")
            await client.disconnect()
            return
        
        # Send code
        await client.send_code_request(PHONE_NUMBER)
        print("SMS code sent to your phone!")
        print(f"Enter the code in this file: {CODE_FILE}")
        print("Then run this script again.")
        
        # Check for code file
        if CODE_FILE.exists():
            code = CODE_FILE.read_text().strip()
            if code:
                print(f"Using code: {code}")
                await client.sign_in(PHONE_NUMBER, code)
                print("✅ Authorized!")
                CODE_FILE.unlink()  # Delete code file
            else:
                print("Code file is empty")
        else:
            # Create empty code file
            CODE_FILE.write_text("")
            print(f"\nCreated {CODE_FILE}")
            print("Paste the SMS code there and run again")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

asyncio.run(main())