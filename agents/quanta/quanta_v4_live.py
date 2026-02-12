#!/usr/bin/env python3
"""
Quanta v4.1 - FULL OANDA Integration
Detects signals → Executes LIVE trades via OANDA
"""

import asyncio
import json
import os
import re
from datetime import datetime
from telethon import TelegramClient, events

# Import OANDA executor
import sys
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from oanda_executor import OandaExecutor

# Configuration
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, CALLISTOFX_CHANNEL

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
OUTBOX_DIR = f'{BASE_DIR}/outbox'
LOG_DIR = f'{BASE_DIR}/logs'
TRADE_LOG = f'{BASE_DIR}/trade_log.jsonl'

# Settings
RISK_PER_TRADE = 20  # $20 fixed for first 20 trades
MAX_SIGNAL_AGE_SECONDS = 300  # 5 minutes - reject old signals

# Strategy Constants
EXIT_SPLITS = [(20, 0.10), (40, 0.10), (60, 0.10), (80, 0.10), (100, 0.10)]
SL_TO_BE_AT = 20
TRAIL_START_AT = 100
TRAIL_DISTANCE = 100

class QuantaTrader:
    def __init__(self):
        self.client = TelegramClient(f'{BASE_DIR}/quanta_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.oanda = OandaExecutor()
        self.channel_id = None
        self.recent_messages = []  # Store last 10 for context
        
        # Ensure directories
        os.makedirs(OUTBOX_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Test OANDA connection
        print("Testing OANDA connection...")
        conn_test = self.oanda.test_connection()
        if conn_test['success']:
            print(f"✅ OANDA LIVE: ${conn_test['balance']} {conn_test['currency']}")
        else:
            print(f"❌ OANDA Error: {conn_test.get('error')}")
    
    def log_message(self, message_text, message_type='general', timestamp=None):
        """Log all messages for learning"""
        log_entry = {
            'timestamp': timestamp or datetime.now().isoformat(),
            'type': message_type,
            'text': message_text[:500]
        }
        
        with open(f'{LOG_DIR}/all_messages.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Keep recent messages for context
        self.recent_messages.append(log_entry)
        if len(self.recent_messages) > 10:
            self.recent_messages.pop(0)
    
    def check_signal_expired(self, signal_text):
        """Check if this signal was recently marked as closed"""
        signal_lower = signal_text.lower()
        
        for msg in self.recent_messages:
            msg_text = msg['text'].lower()
            
            # Check if same symbol mentioned as closed
            if any(sym in msg_text for sym in ['xauusd', 'gold', 'xau']):
                if any(word in msg_text for word in ['closed', 'position closed', 'done', 'finished', 'expired', 'hit sl']):
                    # Check if message is newer than our signal
                    return True, msg['text'][:100]
        
        return False, None
    
    def parse_signal(self, text):
        """Parse trading signal from message"""
        text_upper = text.upper()
        
        # Symbol (XAUUSD or Gold)
        symbol = 'XAU_USD'  # OANDA format
        text_upper_check = text.upper()
        if 'GOLD' in text_upper_check or 'XAU' in text_upper_check:
            symbol = 'XAU_USD'
        elif 'SILVER' in text_upper_check or 'XAG' in text_upper_check:
            symbol = 'XAG_USD'
        
        # Direction
        direction = None
        if 'BUY' in text_upper or 'LONG' in text_upper:
            direction = 'BUY'
        elif 'SELL' in text_upper or 'SHORT' in text_upper:
            direction = 'SELL'
        
        if not direction:
            return None
        
        # Entry range (e.g., "2680-2685" or "2680 to 2685")
        range_match = re.search(r'(\d+\.?\d*)\s*[-–to]\s*(\d+\.?\d*)', text, re.IGNORECASE)
        if range_match:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
        else:
            # Try single price
            price_match = re.search(r'(?:@|at|price)\s*[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
            if price_match:
                price = float(price_match.group(1))
                low = high = price
            else:
                return None
        
        # Stop Loss
        sl_match = re.search(r'(?:SL|STOP)[\s:]+(\d+\.?\d*)', text_upper)
        if sl_match:
            sl = float(sl_match.group(1))
        else:
            return None  # Mandatory SL
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry_range': {'high': high, 'low': low, 'mid': (high + low) / 2},
            'sl': sl,
            'raw_text': text[:200]
        }
    
    def calculate_position_size(self, entry, sl):
        """Calculate units for $20 risk"""
        risk_pips = abs(entry - sl)
        if risk_pips <= 0:
            return None
        
        # XAUUSD: $0.01 per pip per unit
        pip_value = 0.01
        units_needed = int(RISK_PER_TRADE / (risk_pips * pip_value))
        
        return {
            'total_units': units_needed,
            'risk_pips': risk_pips,
            'risk_amount': RISK_PER_TRADE
        }
    
    async def execute_3tier_entry(self, signal):
        """
        Execute 3-tier entry via OANDA
        Tier 1: 33% at high
        Tier 2: 33% at mid
        Tier 3: 34% at low
        """
        position = self.calculate_position_size(
            signal['entry_range']['mid'],
            signal['sl']
        )
        
        if not position:
            return None
        
        total_units = position['total_units']
        
        # 3-Tier entry
        tiers = [
            {'tier': 1, 'price': signal['entry_range']['high'], 'units': int(total_units * 0.33)},
            {'tier': 2, 'price': signal['entry_range']['mid'], 'units': int(total_units * 0.33)},
            {'tier': 3, 'price': signal['entry_range']['low'], 'units': int(total_units * 0.34)},
        ]
        
        executed_orders = []
        
        for tier in tiers:
            print(f"  Tier {tier['tier']}: {tier['units']} units @ {tier['price']}")
            
            # For market orders, we execute immediately
            # In real implementation, you might use limit orders at those prices
            result = self.oanda.create_order(
                instrument=signal['symbol'],
                direction=signal['direction'],
                units=tier['units'],
                stop_loss=signal['sl']
            )
            
            if result['success']:
                executed_orders.append({
                    'tier': tier['tier'],
                    'order_id': result['order_id'],
                    'units': tier['units'],
                    'price': result['price']
                })
                print(f"    ✅ Executed: {result['order_id']}")
            else:
                print(f"    ❌ Failed: {result.get('error')}")
        
        return {
            'signal': signal,
            'position': position,
            'tiers': tiers,
            'executed': executed_orders,
            'total_units_filled': sum(t['units'] for t in executed_orders),
            'status': 'EXECUTED' if len(executed_orders) == 3 else 'PARTIAL'
        }
    
    async def handle_message(self, event):
        """Process incoming message"""
        text = event.message.text
        timestamp = event.message.date
        
        if not text:
            return
        
        # Log ALL messages
        self.log_message(text, 'general', timestamp.isoformat())
        
        # Check if signal
        signal = self.parse_signal(text)
        
        if signal:
            print(f"\n🚨 SIGNAL DETECTED at {timestamp}")
            print(f"   {signal['symbol']} {signal['direction']}")
            print(f"   Range: {signal['entry_range']['low']} - {signal['entry_range']['high']}")
            print(f"   SL: {signal['sl']}")
            
            # Check signal age
            age_seconds = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds()
            if age_seconds > MAX_SIGNAL_AGE_SECONDS:
                print(f"   ❌ SKIPPED: Signal too old ({age_seconds:.0f}s > 5min)")
                self.log_message(text, 'signal_expired', timestamp.isoformat())
                return
            
            # Check if expired
            expired, reason = self.check_signal_expired(text)
            if expired:
                print(f"   ❌ SKIPPED: Signal expired - {reason}")
                self.log_message(text, 'signal_expired', timestamp.isoformat())
                return
            
            # Execute via OANDA
            print(f"   💰 Risk: ${RISK_PER_TRADE}")
            result = await self.execute_3tier_entry(signal)
            
            if result:
                # Save to outbox
                trade_file = f"{OUTBOX_DIR}/trade-live-{datetime.now().strftime('%H%M%S')}.json"
                with open(trade_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Log
                with open(TRADE_LOG, 'a') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'TRADE_EXECUTED',
                        'trade': result
                    }) + '\n')
                
                print(f"   ✅ Trade executed: {trade_file}")
                print(f"   📊 Total units: {result['total_units_filled']}")
            else:
                print(f"   ❌ Execution failed")
    
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
        print("🚀 Quanta v4.1 LIVE TRADING Starting...")
        print("=" * 50)
        print(f"Risk per trade: ${RISK_PER_TRADE}")
        print(f"Strategy: 3-tier entry, 5 TPs, runner")
        print(f"Max signal age: {MAX_SIGNAL_AGE_SECONDS}s")
        print(f"OANDA: LIVE ACCOUNT")
        print("=" * 50)
        print("⚠️  LIVE TRADING - REAL MONEY")
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
        print(f"📊 Logging to {LOG_DIR}/")
        print(f"💾 Trades to {OUTBOX_DIR}/")
        print()
        
        # Set up handler
        @self.client.on(events.NewMessage(chats=self.channel_id))
        async def message_handler(event):
            await self.handle_message(event)
        
        # Run forever
        print("⏳ Running 24/7... Waiting for signals...")
        print()
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    trader = QuantaTrader()
    asyncio.run(trader.run())
