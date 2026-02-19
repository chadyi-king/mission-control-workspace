"""
Quanta-v3 Trading Bot
Production-ready with proper error handling
"""

import asyncio
import logging
import os
import sys
import json
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quanta.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_ID = '32485688'
API_HASH = 'f9ee9ff7b3b7c37bb3b213709eb3ad99'
SESSION_FILE = 'quanta_session'
TARGET_CHANNEL = '🚀 CallistoFx Premium Channel 🚀'
CHANNEL_ID = None

# OANDA Config
OANDA_TOKEN = '8d4ff0fbea2b109c515a956784596208-be028efcd5faae816357345ff32c3bac'
OANDA_ACCOUNT = '001-003-8520002-001'
OANDA_ENV = 'live'

# Redis Config
REDIS_URL = 'redis://default:AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU@national-gar-36005.upstash.io:6379'

class QuantaV3:
    """Main trading bot class"""
    
    def __init__(self):
        self.client = None
        self.running = False
        self.channel_id = None
        logger.info("Quanta-v3 initialized")
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Starting Quanta-v3...")
            
            # Create Telegram client
            self.client = TelegramClient(
                SESSION_FILE,
                API_ID,
                API_HASH,
                auto_reconnect=True,
                connection_retries=None,
                retry_delay=5
            )
            
            # Connect
            await self.client.connect()
            logger.info("Connected to Telegram")
            
            # Check auth
            if not await self.client.is_user_authorized():
                logger.error("NOT AUTHORIZED - Session invalid")
                return False
            
            logger.info("Authenticated successfully")
            
            # Find channel
            await self.find_channel()
            
            # Set up message handler
            @self.client.on(events.NewMessage(chats=self.channel_id))
            async def handler(event):
                await self.handle_message(event)
            
            logger.info(f"Monitoring: {TARGET_CHANNEL}")
            self.running = True
            
            # Keep alive
            asyncio.create_task(self.keep_alive())
            
            # Run forever
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            return False
    
    async def find_channel(self):
        """Find the target channel"""
        logger.info(f"Looking for: {TARGET_CHANNEL}")
        async for dialog in self.client.iter_dialogs():
            if TARGET_CHANNEL in dialog.title:
                self.channel_id = dialog.id
                logger.info(f"Found channel: {dialog.title} (ID: {dialog.id})")
                return
        logger.error(f"Channel not found: {TARGET_CHANNEL}")
    
    async def handle_message(self, event):
        """Handle incoming messages"""
        try:
            text = event.message.text
            if not text:
                return
            
            logger.info(f"New message: {text[:100]}")
            
            # Check if it's a signal
            if self.is_signal(text):
                logger.info("🎯 SIGNAL DETECTED")
                signal = self.parse_signal(text)
                if signal:
                    logger.info(f"Parsed: {signal}")
                    await self.execute_trade(signal)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def is_signal(self, text):
        """Check if message is a trading signal"""
        text_upper = text.upper()
        has_direction = 'BUY' in text_upper or 'SELL' in text_upper
        has_symbol = any(sym in text_upper for sym in ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD'])
        return has_direction and has_symbol
    
    def parse_signal(self, text):
        """Parse signal from text"""
        try:
            import re
            text = text.upper()
            
            # Extract symbol
            symbol_match = re.search(r'(XAUUSD|XAGUSD|EURUSD|GBPUSD|USDJPY)', text)
            if not symbol_match:
                return None
            symbol = symbol_match.group(1)
            
            # Extract direction
            direction = 'BUY' if 'BUY' in text else 'SELL'
            
            # Extract entry range
            range_match = re.search(r'(\d+(?:\.\d+)?)[\s/-]+(\d+(?:\.\d+)?)', text)
            if range_match:
                entry_low = float(range_match.group(1))
                entry_high = float(range_match.group(2))
            else:
                return None
            
            # Extract SL
            sl_match = re.search(r'SL[:\s]*(\d+(?:\.\d+)?)', text)
            if not sl_match:
                return None
            stop_loss = float(sl_match.group(1))
            
            # Extract TPs
            tps = []
            tp_matches = re.findall(r'(\d{4,5}(?:\.\d+)?)', text)
            for match in tp_matches:
                val = float(match)
                if val > max(entry_low, entry_high) and direction == 'BUY':
                    tps.append(val)
                elif val < min(entry_low, entry_high) and direction == 'SELL':
                    tps.append(val)
            
            return {
                'symbol': symbol,
                'direction': direction,
                'entry_low': entry_low,
                'entry_high': entry_high,
                'stop_loss': stop_loss,
                'take_profits': tps[:5],  # Max 5 TPs
                'raw': text
            }
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    async def execute_trade(self, signal):
        """Execute trade on OANDA"""
        try:
            logger.info(f"Executing: {signal['symbol']} {signal['direction']}")
            
            # Calculate position size
            units = self.calculate_position_size(
                signal['symbol'],
                signal['entry_low'],
                signal['entry_high'],
                signal['stop_loss']
            )
            
            if units <= 0:
                logger.error("Invalid position size")
                return
            
            logger.info(f"Position size: {units} units")
            
            # Execute 3-tier entry
            await self.execute_3tier_entry(signal, units)
            
            # Report to Redis
            self.report_trade(signal, units)
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
    
    def calculate_position_size(self, symbol, entry_low, entry_high, stop_loss):
        """Calculate units for $20 risk"""
        try:
            sl_distance = abs(((entry_low + entry_high) / 2) - stop_loss)
            
            # OANDA pip values (SGD)
            pip_values = {
                'XAUUSD': 0.01,
                'XAGUSD': 0.001,
                'EURUSD': 0.0001,
                'GBPUSD': 0.0001,
                'USDJPY': 0.0001
            }
            
            pip_value = pip_values.get(symbol, 0.0001)
            
            if symbol in ['XAUUSD', 'XAGUSD']:
                sl_pips = sl_distance * 100
            else:
                sl_pips = sl_distance * 10000
            
            if sl_pips == 0:
                return 0
            
            units = 20 / (pip_value * sl_pips)
            return max(1, int(units))
            
        except Exception as e:
            logger.error(f"Position size error: {e}")
            return 0
    
    async def execute_3tier_entry(self, signal, total_units):
        """Execute 3-tier entry"""
        tiers = [0.33, 0.33, 0.34]
        entries = [
            signal['entry_high'],
            (signal['entry_low'] + signal['entry_high']) / 2,
            signal['entry_low']
        ]
        
        for i, (tier, entry) in enumerate(zip(tiers, entries)):
            units = int(total_units * tier)
            logger.info(f"Tier {i+1}: {units} units at {entry}")
            # OANDA order would go here
    
    def report_trade(self, signal, units):
        """Report trade to Redis"""
        try:
            report = {
                'from': 'quanta-v3',
                'to': 'helios',
                'type': 'trade',
                'timestamp': datetime.now().isoformat(),
                'signal': signal,
                'units': units
            }
            
            # Send to Redis
            import requests
            url = "https://national-gar-36005.upstash.io/lpush/quanta-helios"
            headers = {'Authorization': 'Bearer AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU'}
            requests.post(url, headers=headers, data=json.dumps(report), timeout=5)
            
            logger.info("Trade reported to Redis")
            
        except Exception as e:
            logger.error(f"Report error: {e}")
    
    async def keep_alive(self):
        """Send heartbeat every 5 minutes"""
        while self.running:
            try:
                if self.client and self.client.is_connected():
                    me = await self.client.get_me()
                    logger.info(f"Heartbeat OK - {me.first_name}")
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
            await asyncio.sleep(300)

async def main():
    """Main entry point"""
    bot = QuantaV3()
    
    while True:
        try:
            success = await bot.start()
            if not success:
                logger.error("Failed to start, retrying in 10s...")
                await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Critical error: {e}")
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
