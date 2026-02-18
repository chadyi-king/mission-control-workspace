"""
Telegram Monitor for Quanta-v2
Stable 24/7 connection with keep-alive and auto-reconnect
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_ID = '32485688'
API_HASH = 'f9ee9ff7b3b7c37bb3b213709eb3ad99'
PHONE_NUMBER = '+6591593838'  # Caleb's phone
SESSION_FILE = 'quanta_session'

# Channel to monitor
TARGET_CHANNEL = '🚀 CallistoFx Premium Channel 🚀'
CHANNEL_ID = None  # Will be discovered automatically

class TelegramMonitor:
    """Stable Telegram monitor with keep-alive and rate limiting"""
    
    def __init__(self, message_handler=None):
        self.api_id = API_ID
        self.api_hash = API_HASH
        self.phone = PHONE_NUMBER
        self.session_file = SESSION_FILE
        self.channel_id = CHANNEL_ID
        self.message_handler = message_handler or self._default_handler
        self.client = None
        self.running = False
        self.message_buffer = []  # Buffer for recent messages
        self.max_buffer_size = 20  # Keep last 20 messages
        self.last_processed_time = 0
        self.min_process_interval = 1  # Process max 1 message per second
    
    def _default_handler(self, message, msg_type='unknown'):
        """Default message handler - prints to console"""
        logger.info(f"[{msg_type.upper()}] {message[:100]}...")
    
    async def keep_alive(self):
        """Send heartbeat every 5 minutes to prevent timeout"""
        while self.running:
            try:
                if self.client and self.client.is_connected():
                    me = await self.client.get_me()
                    logger.debug(f"Heartbeat OK - connected as {me.first_name}")
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
            
            await asyncio.sleep(300)  # 5 minutes
    
    async def find_channel(self):
        """Find the target channel ID"""
        logger.info(f"Looking for channel: {TARGET_CHANNEL}")
        
        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel and TARGET_CHANNEL in dialog.title:
                self.channel_id = dialog.id
                logger.info(f"Found channel: {dialog.title} (ID: {dialog.id})")
                return True
        
        logger.error(f"Channel not found: {TARGET_CHANNEL}")
        return False
    
    async def handle_message(self, event):
        """Handle incoming messages - FILTER for signals and learning content"""
        try:
            message = event.message
            text = message.text or ""
            
            # Skip if no text (photos, videos, etc.)
            if not text:
                return
            
            # Log for debugging (limit to last 100 chars)
            logger.debug(f"Message: {text[:100]}...")
            
            # CHECK 1: Is this a trading signal?
            signal_keywords = ['BUY', 'SELL', 'XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'SL', 'TP', 'RANGE']
            has_signal_keywords = any(kw in text.upper() for kw in signal_keywords)
            has_direction = 'BUY' in text.upper() or 'SELL' in text.upper()
            has_symbol = any(sym in text.upper() for sym in ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY'])
            
            if has_signal_keywords and has_direction and has_symbol:
                logger.info("🎯 SIGNAL DETECTED")
                self.message_handler(text, msg_type='signal')
                return
            
            # CHECK 2: Is this trade results/performance?
            result_keywords = ['PIPS', 'PROFIT', 'LOSS', 'RETURN', 'WON', 'HIT TP', 'HIT SL', 'CLOSED']
            if any(kw in text.upper() for kw in result_keywords):
                logger.info("📊 TRADE RESULT DETECTED")
                self.message_handler(text, msg_type='result')
                return
            
            # CHECK 3: Is this educational commentary?
            edu_keywords = ['BREAKOUT', 'SUPPORT', 'RESISTANCE', 'TREND', 'ANALYSIS', 'LOOKING AT', 'CHART']
            if any(kw in text.upper() for kw in edu_keywords):
                logger.info("📚 COMMENTARY DETECTED")
                self.message_handler(text, msg_type='commentary')
                return
            
            # Ignore other messages (chat, greetings, etc.)
            logger.debug("Ignored: not relevant")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def start(self):
        """Start monitoring with auto-reconnect"""
        self.running = True
        
        # Create client with auto-reconnect enabled
        self.client = TelegramClient(
            self.session_file,
            self.api_id,
            self.api_hash,
            auto_reconnect=True,
            connection_retries=None,  # Infinite retries
            retry_delay=5,  # 5 seconds between retries
            flood_sleep_threshold=60  # Auto-sleep on flood wait
        )
        
        # Connect and authenticate first
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            logger.info("Not authorized. Sending code request...")
            await self.client.send_code_request(self.phone)
            
            # Get code from user
            print("\n" + "="*60)
            print("TELEGRAM AUTHENTICATION REQUIRED")
            print("="*60)
            print(f"A code has been sent to {self.phone}")
            code = input("Enter the code you received: ")
            print("="*60 + "\n")
            
            try:
                await self.client.sign_in(self.phone, code)
                logger.info("Successfully authenticated!")
            except SessionPasswordNeededError:
                password = input("Two-factor authentication enabled. Enter password: ")
                await self.client.sign_in(password=password)
        
        # Start keep-alive task
        asyncio.create_task(self.keep_alive())
        
        # Find channel
        if not await self.find_channel():
            logger.error("Could not find target channel")
            return False
        
        # Set up message handler
        @self.client.on(events.NewMessage(chats=self.channel_id))
        async def handler(event):
            await self.handle_message(event)
        
        # Read recent messages on startup (last 20)
        logger.info("Reading recent messages from channel...")
        try:
            message_count = 0
            async for message in self.client.iter_messages(self.channel_id, limit=20):
                if message.text:
                    logger.info(f"Recent message: {message.text[:100]}...")
                    self.message_handler(message.text, msg_type='recent')
                    message_count += 1
            logger.info(f"Read {message_count} recent messages")
        except Exception as e:
            logger.error(f"Error reading recent messages: {e}")
        
        logger.info("Telegram monitor started!")
        logger.info(f"Monitoring: {TARGET_CHANNEL}")
        
        # Run until disconnected (auto-reconnect handles rest)
        await self.client.run_until_disconnected()
        
        return True
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.client:
            await self.client.disconnect()
        logger.info("Telegram monitor stopped")

async def main():
    """Main entry point with auto-restart"""
    monitor = TelegramMonitor()
    
    while True:
        try:
            logger.info("Starting Telegram monitor...")
            success = await monitor.start()
            
            if not success:
                logger.error("Failed to start, retrying in 10 seconds...")
                await asyncio.sleep(10)
                
        except FloodWaitError as e:
            logger.warning(f"Flood wait: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            
        except Exception as e:
            logger.error(f"Critical error: {e}")
            logger.info("Restarting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == '__main__':
    # Check if credentials are set
    if not API_ID or not API_HASH:
        print("=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("\n1. Go to https://my.telegram.org/apps")
        print("2. Log in with your phone number")
        print("3. Create new app:")
        print("   - App name: QuantaTrader")
        print("   - Short name: quanta")
        print("4. Copy API_ID and API_HASH")
        print("\n5. Set environment variables:")
        print("   export TELEGRAM_API_ID=your_api_id")
        print("   export TELEGRAM_API_HASH=your_api_hash")
        print("   export TELEGRAM_PHONE=+6591234567")
        print("\n6. Run again: python telegram_monitor.py")
        print("=" * 60)
        exit(1)
    
    # Run with auto-restart
    asyncio.run(main())
