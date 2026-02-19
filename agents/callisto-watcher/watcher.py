#!/usr/bin/env python3
"""
CallistoFX Watcher - 24/7 Telegram Monitor
Watches Caleb's personal Telegram for CallistoFX signals
"""

import os
import json
import re
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import redis

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Config
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION = os.getenv('TELEGRAM_SESSION')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '🚀 CallistoFx Premium Channel 🚀')
REDIS_URL = os.getenv('REDIS_URL')

# Redis setup
r = redis.from_url(REDIS_URL) if REDIS_URL else None

# Signal patterns
SIGNAL_PATTERNS = [
    # Pattern: EURUSD BUY @ 1.0850 SL 1.0800 TP 1.0900
    r'(\w{6,7})\s+(BUY|SELL)\s+[@\s]+([\d.]+).*?SL\s+([\d.]+).*?TP\s+([\d.]+)',
    # Pattern: Buy EURUSD 1.0850 | SL: 1.0800 | TP: 1.0900
    r'(BUY|SELL)\s+(\w{6,7})\s+([\d.]+).*?SL[:\s]+([\d.]+).*?TP[:\s]+([\d.]+)',
]


def parse_signal(text):
    """Extract trading signal from message text."""
    text = text.upper().replace(',', '')
    
    for pattern in SIGNAL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 5:
                # Check order of groups
                if groups[0] in ['BUY', 'SELL']:
                    direction, pair, entry, sl, tp = groups
                else:
                    pair, direction, entry, sl, tp = groups
                
                return {
                    'pair': pair.upper(),
                    'direction': direction.upper(),
                    'entry': float(entry),
                    'stop_loss': float(sl),
                    'take_profit': float(tp),
                    'raw_message': text[:500]  # First 500 chars
                }
    
    return None


def send_to_redis(signal):
    """Send parsed signal to Redis for Quanta."""
    if not r:
        logger.error("Redis not connected")
        return False
    
    message = {
        'from': 'callisto',
        'to': 'quanta',
        'type': 'signal',
        'timestamp': datetime.now().isoformat(),
        'signal': signal
    }
    
    try:
        r.lpush('callisto→quanta', json.dumps(message))
        logger.info(f"Signal sent to Redis: {signal['pair']} {signal['direction']}")
        return True
    except Exception as e:
        logger.error(f"Failed to send to Redis: {e}")
        return False


def report_status(status, message=""):
    """Report watcher status to Helios."""
    if not r:
        return
    
    try:
        report = {
            'from': 'callisto',
            'to': 'helios',
            'type': 'status',
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message
        }
        r.lpush('callisto→helios', json.dumps(report))
    except Exception as e:
        logger.error(f"Failed to report status: {e}")


async def main():
    """Main watcher loop."""
    logger.info("Starting CallistoFX Watcher...")
    
    if not SESSION:
        logger.error("No TELEGRAM_SESSION found! Run session_generator.py first.")
        return
    
    if not r:
        logger.error("No REDIS_URL found! Set environment variable.")
        return
    
    # Create client
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    
    @client.on(events.NewMessage(chats=TARGET_CHANNEL))
    async def handler(event):
        """Handle new messages in target channel."""
        message_text = event.message.message
        logger.info(f"New message in {TARGET_CHANNEL}")
        
        # Try to parse signal
        signal = parse_signal(message_text)
        
        if signal:
            logger.info(f"Signal detected: {signal}")
            send_to_redis(signal)
        else:
            logger.debug("No signal pattern found in message")
    
    # Connect
    await client.start()
    logger.info(f"Connected! Watching: {TARGET_CHANNEL}")
    report_status('active', f'Watching {TARGET_CHANNEL}')
    
    # Keep running
    try:
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Disconnected: {e}")
        report_status('error', str(e))
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
