#!/usr/bin/env python3
"""
Quanta Signal Monitor - Trading Bot
Monitors Telegram for CallistoFx signals and executes via OANDA
"""

import json
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Telegram client (will use telethon)
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import Message
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    from typing import Any as Message
    print("Warning: telethon not installed. Run: pip install telethon")

# OANDA API
try:
    import oandapyV20
    from oandapyV20 import API
    from oandapyV20.endpoints.orders import OrderCreate
    from oandapyV20.endpoints.positions import PositionDetails
    OANDA_AVAILABLE = False  # Will enable after credentials added
except ImportError:
    OANDA_AVAILABLE = False
    print("Warning: oandapyV20 not installed. Run: pip install oandapyV20")

# Configuration
CONFIG = {
    "telegram_api_id": 32485688,
    "telegram_api_hash": "f9ee9ff7b3b7c37bb3b213709eb3ad99",
    "phone_number": "+6591593838",
    "session_name": "quanta_session",
    "channel_to_monitor": "🚀 CallistoFx Premium Channel 🚀",
    "oanda_account_id": None,  # Fill from SECRETS.md
    "oanda_api_key": None,     # Fill from SECRETS.md
    "oanda_environment": "practice",  # practice or live
    "risk_percent": 2.0,  # 2% risk per trade
    "default_lots": 0.1,   # Fallback lot size
    "trailing_enabled": True,
    "trailing_activation_tp": 3,  # Activate trailing after TP3
    "trailing_distance_pips": 20,
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quanta_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Quanta')


class SignalParser:
    """Parse CallistoFx signals from Telegram messages"""
    
    # Color emojis
    BUY_EMOJI = "🟢"
    SELL_EMOJI = "🔴"
    
    # Regex patterns
    PATTERNS = {
        'pair': r'[🟢🔴]([A-Z]{6}|XAUUSD|XAGUSD|US30|US100)[🟢🔴]',
        'direction': r'\b(BUY|SELL)\b',
        'range': r'RANGE:\s*(\d+\.?\d*)-(\d+\.?\d*)',
        'sl': r'SL\s+(\d+\.?\d*)',
        'tp': r'TP\s*:\s*(\d+\.?\d*(?:/\d+\.?\d*)*)',
    }
    
    def parse(self, message_text: str) -> Optional[Dict]:
        """Parse a signal message and return structured data"""
        
        if not message_text:
            return None
        
        text = message_text.upper().strip()
        
        # Determine direction from emoji
        direction = None
        if self.BUY_EMOJI in message_text:
            direction = "BUY"
        elif self.SELL_EMOJI in message_text:
            direction = "SELL"
        
        if not direction:
            # Try text pattern
            direction_match = re.search(self.PATTERNS['direction'], text)
            if direction_match:
                direction = direction_match.group(1)
        
        if not direction:
            logger.warning("Could not determine direction from message")
            return None
        
        # Extract pair
        pair_match = re.search(self.PATTERNS['pair'], text)
        if not pair_match:
            logger.warning("Could not find trading pair")
            return None
        
        pair = pair_match.group(1)
        
        # Extract entry range
        range_match = re.search(self.PATTERNS['range'], text)
        if not range_match:
            logger.warning("Could not find entry range")
            return None
        
        entry_min = float(range_match.group(1))
        entry_max = float(range_match.group(2))
        
        # Extract stop loss
        sl_match = re.search(self.PATTERNS['sl'], text)
        if not sl_match:
            logger.warning("Could not find stop loss")
            return None
        
        stop_loss = float(sl_match.group(1))
        
        # Extract take profits
        tp_match = re.search(self.PATTERNS['tp'], text)
        if not tp_match:
            logger.warning("Could not find take profits")
            return None
        
        tp_text = tp_match.group(1)
        take_profits = [float(x.strip()) for x in tp_text.split('/')]
        
        # Validate signal
        if len(take_profits) < 1:
            logger.warning("No take profits found")
            return None
        
        # Calculate risk/reward
        avg_entry = (entry_min + entry_max) / 2
        sl_distance = abs(avg_entry - stop_loss)
        tp_distance = abs(take_profits[0] - avg_entry)
        
        if sl_distance == 0:
            risk_reward = 0
        else:
            risk_reward = tp_distance / sl_distance
        
        return {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'direction': direction,
            'entry_range': [entry_min, entry_max],
            'stop_loss': stop_loss,
            'take_profits': take_profits,
            'avg_entry': avg_entry,
            'sl_distance': sl_distance,
            'risk_reward': round(risk_reward, 2),
            'trailing_enabled': CONFIG['trailing_enabled'],
            'trailing_activation_price': take_profits[CONFIG['trailing_activation_tp'] - 1] 
                if len(take_profits) >= CONFIG['trailing_activation_tp'] else None,
            'raw_message': message_text,
        }
    
    def format_for_alert(self, signal: Dict) -> str:
        """Format signal for human-readable alert"""
        emoji = "🟢" if signal['direction'] == "BUY" else "🔴"
        
        msg = f"""
{emoji} **NEW SIGNAL DETECTED** {emoji}

**Pair:** {signal['pair']}
**Direction:** {signal['direction']}
**Entry Range:** {signal['entry_range'][0]} - {signal['entry_range'][1]}
**Stop Loss:** {signal['stop_loss']}
**Take Profits:** {' / '.join(map(str, signal['take_profits']))}
**Risk/Reward:** 1:{signal['risk_reward']}

**Trailing Stop:** {'Enabled' if signal['trailing_enabled'] else 'Disabled'}
**Trailing activates at:** {signal['trailing_activation_price']}

Execute trade? (Reply: YES or NO)
"""
        return msg.strip()


class OANDATrader:
    """Execute trades via OANDA API"""
    
    def __init__(self, account_id: str, api_key: str, environment: str = "practice"):
        self.account_id = account_id
        self.api_key = api_key
        self.environment = environment
        
        if OANDA_AVAILABLE and account_id and api_key:
            self.api = API(access_token=api_key, environment=environment)
            self.connected = True
        else:
            self.connected = False
            logger.warning("OANDA not connected - missing credentials or library")
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> int:
        """Calculate position size based on 2% risk rule"""
        
        risk_amount = account_balance * (CONFIG['risk_percent'] / 100)
        sl_distance = signal['sl_distance']
        
        # For XAUUSD: 1 unit = $0.01 per pip (roughly)
        # Position size = Risk Amount / (SL Distance * Pip Value)
        pip_value = 0.01  # $0.01 per pip for 1 unit
        
        if sl_distance > 0:
            units = int(risk_amount / (sl_distance * pip_value))
        else:
            units = int(CONFIG['default_lots'] * 100000)  # Convert lots to units
        
        # Cap at reasonable max
        max_units = 10000  # Max 10,000 units
        return min(units, max_units)
    
    def execute_trade(self, signal: Dict) -> Dict:
        """Execute trade on OANDA"""
        
        if not self.connected:
            logger.error("OANDA not connected")
            return {'status': 'error', 'message': 'Not connected to OANDA'}
        
        # Format instrument (XAUUSD -> XAU_USD)
        instrument = signal['pair']
        if '_' not in instrument:
            if instrument == 'XAUUSD':
                instrument = 'XAU_USD'
            elif instrument == 'XAGUSD':
                instrument = 'XAG_USD'
            elif len(instrument) == 6:
                instrument = f"{instrument[:3]}_{instrument[3:]}"
        
        # Determine direction
        units = self.calculate_position_size(signal, 10000)  # Assume $10k balance for now
        if signal['direction'] == 'SELL':
            units = -units
        
        # Build order
        order = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "stopLossOnFill": {
                    "price": str(signal['stop_loss'])
                },
                "takeProfitOnFill": {
                    "price": str(signal['take_profits'][0])  # First TP
                }
            }
        }
        
        try:
            r = OrderCreate(self.account_id, data=order)
            self.api.request(r)
            response = r.response
            
            logger.info(f"Trade executed: {response}")
            return {
                'status': 'success',
                'order_id': response.get('orderFillTransaction', {}).get('id'),
                'units': units,
                'instrument': instrument,
            }
        
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {'status': 'error', 'message': str(e)}


class QuantaMonitor:
    """Main monitor class - connects Telegram to OANDA"""
    
    def __init__(self):
        self.parser = SignalParser()
        self.trader = OANDATrader(
            CONFIG['oanda_account_id'],
            CONFIG['oanda_api_key'],
            CONFIG['oanda_environment']
        )
        self.client = None
        self.signal_log = Path('projects/signals/signal_log.jsonl')
        self.signal_log.parent.mkdir(parents=True, exist_ok=True)
    
    async def start_telegram_client(self):
        """Start Telegram client and listen for messages"""
        
        if not TELETHON_AVAILABLE:
            logger.error("Telethon not installed. Cannot start Telegram client.")
            return
        
        self.client = TelegramClient(
            CONFIG['session_name'],
            CONFIG['telegram_api_id'],
            CONFIG['telegram_api_hash']
        )
        
        @self.client.on(events.NewMessage(chats=CONFIG['channel_to_monitor']))
        async def handler(event):
            await self.handle_new_message(event.message)
        
        await self.client.start(phone=CONFIG['phone_number'])
        logger.info("Quanta Monitor started - listening for signals...")
        await self.client.run_until_disconnected()
    
    async def handle_new_message(self, message: Message):
        """Process new Telegram message"""
        
        text = message.text
        if not text:
            return
        
        logger.info(f"New message received: {text[:50]}...")
        
        # Parse signal
        signal = self.parser.parse(text)
        
        if signal:
            logger.info(f"✅ Signal parsed: {signal['pair']} {signal['direction']}")
            
            # Log signal
            self.log_signal(signal)
            
            # Format alert
            alert = self.parser.format_for_alert(signal)
            
            # TODO: Send alert to CHAD_YI for approval
            # For now, log to file
            logger.info(f"ALERT:\n{alert}")
            
            # Save to outbox for CHAD_YI to pick up
            self.save_to_outbox(signal, alert)
        else:
            logger.debug("Message not a valid signal")
    
    def log_signal(self, signal: Dict):
        """Log signal to JSONL file"""
        with open(self.signal_log, 'a') as f:
            f.write(json.dumps(signal) + '\n')
    
    def save_to_outbox(self, signal: Dict, alert: str):
        """Save signal to outbox for CHAD_YI"""
        outbox_dir = Path('../outbox')
        outbox_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SIGNAL_{signal['pair']}_{timestamp}.json"
        
        data = {
            'type': 'new_signal',
            'signal': signal,
            'alert_formatted': alert,
            'status': 'pending_approval',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(outbox_dir / filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Signal saved to outbox: {filename}")


def test_parser():
    """Test the signal parser with sample messages"""
    
    test_signals = [
        """🟢XAUUSD🟢
BUY
RANGE: 5010-5016.5
SL 4995
TP : 5030/5040/5060/5100""",
        
        """🔴EURUSD🔴
SELL
RANGE: 1.0850-1.0855
SL 1.0870
TP : 1.0830/1.0820/1.0800""",
    ]
    
    parser = SignalParser()
    
    print("=" * 60)
    print("SIGNAL PARSER TEST")
    print("=" * 60)
    
    for i, signal_text in enumerate(test_signals, 1):
        print(f"\n--- Test Signal {i} ---")
        print(signal_text)
        print("\n--- Parsed Result ---")
        
        result = parser.parse(signal_text)
        if result:
            print(json.dumps(result, indent=2))
            print("\n--- Formatted Alert ---")
            print(parser.format_for_alert(result))
        else:
            print("❌ Failed to parse")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run parser tests
        test_parser()
    else:
        # Start monitoring
        print("=" * 60)
        print("QUANTA TRADING MONITOR")
        print("=" * 60)
        print("\nStarting Quanta...")
        print("Note: This requires:")
        print("  1. Telegram authentication (you'll get an SMS code)")
        print("  2. OANDA credentials in SECRETS.md")
        print("  3. Signal channel access")
        print("\nTo test parser only, run: python quanta_monitor.py test")
        print("=" * 60)
        
        monitor = QuantaMonitor()
        
        try:
            import asyncio
            asyncio.run(monitor.start_telegram_client())
        except KeyboardInterrupt:
            print("\n\nQuanta stopped by user.")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise