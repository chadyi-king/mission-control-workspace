#!/usr/bin/env python3
"""
Quanta v4.0 - Full Implementation
- $20 fixed risk
- 3-tier entry
- 5 TPs + runner
- Reads all messages for learning
- Auto-detects SL commands
"""

import asyncio
import json
import os
import re
from datetime import datetime
from telethon import TelegramClient, events

# Configuration
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, CALLISTOFX_CHANNEL

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
OUTBOX_DIR = f'{BASE_DIR}/outbox'
LOG_DIR = f'{BASE_DIR}/logs'
LEARNING_DB = f'{BASE_DIR}/learning_db.json'
TRADE_LOG = f'{BASE_DIR}/trade_log.jsonl'

# Settings
RISK_PER_TRADE = 20  # $20 fixed
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID', '')
OANDA_API_KEY = os.getenv('OANDA_API_KEY', '')

# Strategy Constants
EXIT_SPLITS = [(20, 0.10), (40, 0.10), (60, 0.10), (80, 0.10), (100, 0.10)]
SL_TO_BE_AT = 20
TRAIL_START_AT = 100
TRAIL_DISTANCE = 100
RUNNER_CLOSE_PCT = 0.10
RUNNER_INTERVAL = 50

class QuantaTrader:
    def __init__(self):
        self.client = TelegramClient(f'{BASE_DIR}/quanta_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.channel_id = None
        self.active_trades = []
        self.message_count = 0
        self.signal_count = 0
        
        # Ensure directories
        os.makedirs(OUTBOX_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
    
    def log_message(self, message_text, message_type='general'):
        """Log all messages for learning"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': message_type,
            'text': message_text[:500],  # First 500 chars
            'length': len(message_text)
        }
        
        with open(f'{LOG_DIR}/all_messages.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        self.message_count += 1
    
    def parse_signal(self, text):
        """Parse trading signal from message"""
        text_upper = text.upper()
        
        # Direction
        direction = None
        if 'BUY' in text_upper:
            direction = 'BUY'
        elif 'SELL' in text_upper:
            direction = 'SELL'
        
        if not direction:
            return None
        
        # Symbol (default XAUUSD)
        symbol = 'XAUUSD'
        
        # Entry range (e.g., "2680-2685" or "2680 to 2685")
        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
        if range_match:
            high = float(range_match.group(2))
            low = float(range_match.group(1))
        else:
            return None
        
        # Stop Loss
        sl_match = re.search(r'SL[\s:]+(\d+\.?\d*)', text_upper)
        if sl_match:
            sl = float(sl_match.group(1))
        else:
            return None
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry_range': {'high': high, 'low': low, 'mid': (high + low) / 2},
            'sl': sl,
            'raw_text': text[:200]
        }
    
    def check_sl_command(self, text):
        """Check if message contains SL move command"""
        text_lower = text.lower()
        
        patterns = [
            r'move sl to be',
            r'move sl to breakeven',
            r'shift sl to be',
            r'sl to entry',
            r'stop loss to entry',
            r'protect profits',
            r'lock in',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def calculate_position_size(self, entry, sl):
        """Calculate position size for $20 risk"""
        risk_pips = abs(entry - sl)
        if risk_pips <= 0:
            return None
        
        # XAUUSD: $0.01 per pip per unit
        pip_value = 0.01
        units_needed = RISK_PER_TRADE / (risk_pips * pip_value)
        lots = units_needed / 100
        
        return {
            'total_lots': round(lots, 3),
            'risk_pips': risk_pips,
            'risk_amount': RISK_PER_TRADE
        }
    
    def create_trade_plan(self, signal):
        """Create complete trade execution plan"""
        position = self.calculate_position_size(
            signal['entry_range']['mid'],
            signal['sl']
        )
        
        if not position:
            return None
        
        # 3-tier entry
        total_lots = position['total_lots']
        tiers = [
            {'tier': 1, 'price': signal['entry_range']['high'], 'lots': round(total_lots * 0.33, 3), 'status': 'pending'},
            {'tier': 2, 'price': signal['entry_range']['mid'], 'lots': round(total_lots * 0.33, 3), 'status': 'pending'},
            {'tier': 3, 'price': signal['entry_range']['low'], 'lots': round(total_lots * 0.34, 3), 'status': 'pending'},
        ]
        
        trade = {
            'id': f"{signal['symbol']}-{signal['direction']}-{datetime.now().strftime('%H%M%S')}",
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'entry_range': signal['entry_range'],
            'sl': signal['sl'],
            'tiers': tiers,
            'total_lots': total_lots,
            'risk_amount': RISK_PER_TRADE,
            'status': 'PLANNED',
            'created_at': datetime.now().isoformat(),
            'plan': {
                'entry': '3-tier DCA',
                'sl_management': f'Move to BE at +{SL_TO_BE_AT} pips',
                'tps': [f'+{pips}: {int(pct*100)}%' for pips, pct in EXIT_SPLITS],
                'runner': f'50% from +{TRAIL_START_AT}, close {int(RUNNER_CLOSE_PCT*100)}% every +{RUNNER_INTERVAL} pips, trail {TRAIL_DISTANCE} pips behind'
            }
        }
        
        return trade
    
    async def handle_message(self, event):
        """Process incoming message"""
        text = event.message.text
        if not text:
            return
        
        # Log ALL messages for learning
        self.log_message(text, 'general')
        
        # Check if signal
        signal = self.parse_signal(text)
        
        if signal:
            self.signal_count += 1
            self.log_message(text, 'signal')
            
            print(f"\n🚨 SIGNAL DETECTED")
            print(f"   {signal['symbol']} {signal['direction']}")
            print(f"   Range: {signal['entry_range']['low']} - {signal['entry_range']['high']}")
            print(f"   SL: {signal['sl']}")
            
            # Create trade plan
            trade = self.create_trade_plan(signal)
            
            if trade:
                print(f"   Total Lots: {trade['total_lots']}")
                print(f"   Risk: ${trade['risk_amount']}")
                print(f"   3-Tier Entry: {trade['tiers'][0]['lots']} / {trade['tiers'][1]['lots']} / {trade['tiers'][2]['lots']}")
                
                # Save to outbox
                trade_file = f"{OUTBOX_DIR}/trade-{trade['id']}.json"
                with open(trade_file, 'w') as f:
                    json.dump(trade, f, indent=2)
                
                # Log trade
                with open(TRADE_LOG, 'a') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'SIGNAL_PLANNED',
                        'trade': trade
                    }) + '\n')
                
                # TODO: Execute via OANDA API
                # For now: paper trade mode
                print(f"   📝 Trade plan created: {trade_file}")
                print(f"   ⚠️  Paper trade mode (OANDA execution pending)")
            
        elif self.check_sl_command(text):
            # SL command detected
            self.log_message(text, 'sl_command')
            print(f"\n📢 SL COMMAND DETECTED")
            print(f"   Text: {text[:100]}...")
            print(f"   Action: Move SL to BE")
            
            # TODO: Execute SL move via OANDA
            # For now: log only
            with open(TRADE_LOG, 'a') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'SL_COMMAND_DETECTED',
                    'text': text[:200]
                }) + '\n')
    
    async def find_channel(self):
        """Find CallistoFx channel"""
        print("🔍 Searching for CallistoFx channel...")
        
        async for dialog in self.client.iter_dialogs():
            name = dialog.name or ""
            if "callistofx" in name.lower():
                print(f"✅ Found: {name} (ID: {dialog.id})")
                return dialog.id
        
        return None
    
    async def run(self):
        """Main run loop"""
        print("🚀 Quanta v4.0 Starting...")
        print("=" * 50)
        print(f"Risk per trade: ${RISK_PER_TRADE}")
        print(f"Strategy: 3-tier entry, 5 TPs, runner")
        print(f"Learning: All messages logged")
        print("=" * 50)
        
        # Connect
        await self.client.start(phone=lambda: PHONE_NUMBER)
        me = await self.client.get_me()
        print(f"✅ Logged in as: {me.first_name}")
        
        # Find channel
        self.channel_id = await self.find_channel()
        if not self.channel_id:
            print("❌ Channel not found")
            return
        
        print(f"🎯 Monitoring channel: {self.channel_id}")
        print(f"📊 Logging all messages to {LOG_DIR}/")
        print()
        
        # Set up handler
        @self.client.on(events.NewMessage(chats=self.channel_id))
        async def message_handler(event):
            await self.handle_message(event)
        
        # Run forever
        print("⏳ Running 24/7...")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    trader = QuantaTrader()
    asyncio.run(trader.run())
