#!/usr/bin/env python3
"""
Quanta CALLISTOFX Monitor v4.0 - WITH LIVE TRADE MANAGEMENT

Key Features:
- Captures signals from CallistoFX Telegram
- Executes trades via OANDA
- MONITORS open trades and manages SL/TP automatically
- Moves SL to breakeven at +20 pips
- Locks +20 pips profit at +50 pips
- Trails SL at -50 pips when +100 pips profit
"""

from telethon import TelegramClient, events
import json
import re
import asyncio
import requests
from datetime import datetime, timedelta
import os
import gzip
import glob
from pathlib import Path

# Import OANDA executor for live trade management
import sys
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/agents/quanta')
from oanda_executor import OandaExecutor

# Load configs
from telegram_config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, CALLISTOFX_CHANNEL

# Paths
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents/quanta'
INBOX_DIR = f'{BASE_DIR}/inbox'
OUTBOX_DIR = f'{BASE_DIR}/outbox'
LOG_DIR = f'{BASE_DIR}/logs'
SESSION_FILE = '/tmp/quanta_telegram_session'
ALERTS_FILE = f'{OUTBOX_DIR}/trade_alerts.jsonl'

# Settings
MAX_LOG_DAYS = 7
SIGNAL_LOG_FILE = f'{INBOX_DIR}/signals.jsonl'
TRADING_STATE_FILE = f'{BASE_DIR}/trading_state.json'
OPEN_TRADES_FILE = f'{BASE_DIR}/open_trades.json'
LEARNING_DB_FILE = f'{BASE_DIR}/learning_database.json'
LESSONS_FILE = f'{BASE_DIR}/lessons_learned.jsonl'

# Trading Constants - OANDA ACTUAL VALUES
# Pip values are PER STANDARD LOT (100 units for XAUUSD, 100k for forex)
PIP_VALUES = {
    'XAUUSD': 1.19,   # ~$1.19 SGD per pip per 100 units
    'XAGUSD': 0.15,   # ~$0.15 SGD per pip per 100 units
    'EURUSD': 13.5,   # ~$13.5 SGD per pip per 100k units
    'GBPUSD': 17.0,   # ~$17.0 SGD per pip per 100k units
    'USDJPY': 11.0,   # ~$11.0 SGD per pip per 100k units
}

LOT_SIZES = {
    'XAUUSD': 100,      # 1 lot = 100 units
    'XAGUSD': 100,      # 1 lot = 100 units
    'EURUSD': 100000,   # 1 lot = 100,000 units
    'GBPUSD': 100000,
    'USDJPY': 100000,
}

# Initialize client - use existing authenticated session
SESSION_FILE = '/home/chad-yi/.openclaw/workspace/agents/quanta/quanta_session'
client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Ensure directories exist
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

class TradingState:
    """Manages trading state: balance, daily stats, open trades"""
    
    def __init__(self):
        self.initial_balance = 2000
        self.current_balance = 2000
        self.risk_percent = 2
        self.max_daily_risk = 6
        self.max_concurrent_trades = 2
        self.max_trades_per_day = 5
        
        self.today = datetime.now().date()
        self.daily_stats = {
            'trades_taken': 0,
            'risk_used_percent': 0,
            'pnl': 0,
            'trades': []
        }
        
        self.open_trades = []
        self.load_state()
    
    def load_state(self):
        """Load state from file"""
        if os.path.exists(TRADING_STATE_FILE):
            with open(TRADING_STATE_FILE) as f:
                data = json.load(f)
                self.current_balance = data.get('current_balance', self.initial_balance)
                saved_date = datetime.fromisoformat(data.get('date', self.today.isoformat())).date()
                
                if saved_date == self.today:
                    self.daily_stats = data.get('daily_stats', self.daily_stats)
                    self.open_trades = data.get('open_trades', [])
    
    def save_state(self):
        """Save state to file"""
        data = {
            'current_balance': self.current_balance,
            'date': self.today.isoformat(),
            'daily_stats': self.daily_stats,
            'open_trades': self.open_trades,
            'initial_balance': self.initial_balance
        }
        with open(TRADING_STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_risk_amount(self):
        """Fixed risk per trade: $20 (as requested by Caleb)"""
        return 20.0  # Fixed $20 risk per trade
    
    def can_trade(self):
        """Check if we can take a new trade"""
        if self.daily_stats['risk_used_percent'] >= self.max_daily_risk:
            print(f"❌ Daily risk limit reached: {self.daily_stats['risk_used_percent']}%")
            return False
        
        if len(self.open_trades) >= self.max_concurrent_trades:
            print(f"❌ Max concurrent trades reached: {len(self.open_trades)}")
            return False
        
        if self.daily_stats['trades_taken'] >= self.max_trades_per_day:
            print(f"❌ Max daily trades reached: {self.daily_stats['trades_taken']}")
            return False
        
        return True
    
    def record_trade(self, trade_info):
        """Record a new trade"""
        self.daily_stats['trades_taken'] += 1
        self.daily_stats['risk_used_percent'] += self.risk_percent
        self.daily_stats['trades'].append(trade_info)
        self.open_trades.append(trade_info)
        self.save_state()
    
    def update_balance(self, pnl):
        """Update balance after trade closes"""
        self.current_balance += pnl
        self.daily_stats['pnl'] += pnl
        self.save_state()
        print(f"💰 Balance updated: ${self.current_balance:.2f} (PnL: ${pnl:+.2f})")


class SignalParser:
    """Parse trading signals from CallistoFx"""
    
    @staticmethod
    def parse_signal(text):
        """Parse CallistoFx signal format"""
        if not text:
            return None
        
        signal = {
            'raw_text': text,
            'parsed_at': datetime.now().isoformat()
        }
        
        text_upper = text.upper()
        
        # Direction: BUY or SELL
        if 'BUY' in text_upper:
            signal['direction'] = 'BUY'
        elif 'SELL' in text_upper:
            signal['direction'] = 'SELL'
        else:
            return None
        
        # Symbol
        symbols = ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100']
        for sym in symbols:
            if sym in text_upper:
                signal['symbol'] = sym
                break
        
        if 'symbol' not in signal:
            return None
        
        # Entry range
        range_match = re.search(r'(?:Buy Range:|Sell Range:)?\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
        if range_match:
            high = float(range_match.group(1))
            low = float(range_match.group(2))
            signal['entry_range'] = {'high': high, 'low': low, 'mid': (high + low) / 2}
        else:
            price_match = re.search(r'(?:@|at|price)\s*[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
            if price_match:
                price = float(price_match.group(1))
                signal['entry_range'] = {'high': price, 'low': price, 'mid': price}
            else:
                return None
        
        # Stop Loss
        sl_match = re.search(r'SL[:\s]+(\d+\.?\d*)', text_upper)
        if sl_match:
            signal['sl'] = float(sl_match.group(1))
        else:
            return None
        
        # Take Profits
        tp_matches = re.findall(r'(?:TP\d*[\s:]+|Target[\s:]+)(\d+\.?\d*)', text_upper)
        if tp_matches:
            signal['tps'] = [float(tp) for tp in tp_matches]
            while len(signal['tps']) < 5:
                last_tp = signal['tps'][-1]
                if signal['direction'] == 'BUY':
                    signal['tps'].append(last_tp + 20)
                else:
                    signal['tps'].append(last_tp - 20)
        else:
            return None
        
        return signal
    
    @staticmethod
    def calculate_signal_score(signal, context):
        """Calculate signal quality score (0-100)"""
        score = 0
        score += 40  # Base score
        
        entry = signal['entry_range']['mid']
        sl = signal['sl']
        tp1 = signal['tps'][0]
        
        if signal['direction'] == 'BUY':
            risk = abs(entry - sl)
            reward = abs(tp1 - entry)
        else:
            risk = abs(sl - entry)
            reward = abs(entry - tp1)
        
        rr = reward / risk if risk > 0 else 0
        
        if rr >= 3:
            score += 15
        elif rr >= 2:
            score += 10
        elif rr >= 1:
            score += 5
        
        if signal['symbol'] == 'XAUUSD':
            score += 10
        
        signal['score'] = score
        signal['rr'] = round(rr, 2)
        
        return score


class LearningDatabase:
    """
    Tracks trading lessons from CallistoFX and correlates with outcomes.
    Learns WHY they took trades and whether it worked.
    """
    
    def __init__(self):
        self.db_file = LEARNING_DB_FILE
        self.lessons_file = LESSONS_FILE
        self.patterns = {}
        self.strategies = {}
        self.outcomes = []
        self.load()
    
    def load(self):
        """Load learning database"""
        if os.path.exists(self.db_file):
            with open(self.db_file) as f:
                data = json.load(f)
                self.patterns = data.get('patterns', {})
                self.strategies = data.get('strategies', {})
                self.outcomes = data.get('outcomes', [])
    
    def save(self):
        """Save learning database"""
        data = {
            'patterns': self.patterns,
            'strategies': self.strategies,
            'outcomes': self.outcomes,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def parse_lesson(text):
        """
        Extract educational content from CallistoFX messages.
        Parses analysis, reasoning, patterns, and teachings.
        """
        lesson = {
            'raw_text': text,
            'parsed_at': datetime.now().isoformat(),
            'has_lesson': False
        }
        
        # Look for analysis/reasoning sections
        analysis_patterns = [
            r'[Aa]nalysis[\s:]+([^\n]+)',
            r'[Ww]hy[\s:]+([^\n]+)',
            r'[Rr]eason[\s:]+([^\n]+)',
            r'[Ss]etup[\s:]+([^\n]+)',
            r'[Pp]attern[\s:]+([^\n]+)',
            r'[Ss]trategy[\s:]+([^\n]+)',
            r'[Bb]ecause[\s:]+([^\n]+)',
            r'[Tt]echnical[\s:]+([^\n]+)',
            r'[Ff]undamental[\s:]+([^\n]+)',
            r'[Ss]upport[\s:]+([^\n]+)',
            r'[Rr]esistance[\s:]+([^\n]+)',
            r'[Tt]rend[\s:]+([^\n]+)',
            r'[Bb]reakout[\s:]+([^\n]+)',
            r'[Rr]et[r]?acement[\s:]+([^\n]+)',
        ]
        
        analysis_found = []
        for pattern in analysis_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis_found.extend(matches)
        
        if analysis_found:
            lesson['has_lesson'] = True
            lesson['analysis'] = analysis_found
        
        # Extract specific patterns mentioned
        pattern_keywords = {
            'engulfing': r'[Bb]ullish engulfing|[Bb]earish engulfing',
            'pin_bar': r'[Pp]in bar|[Ss]hooting star|[Hh]ammer',
            'doji': r'[Dd]oji',
            'support_bounce': r'[Bb]ounce.*support|[Ss]upport.*hold',
            'resistance_break': r'[Bb]reak.*resistance|[Rr]esistance.*break',
            'trend_continuation': r'[Cc]ontinuation|[Tt]rend.*follow',
            'trend_reversal': r'[Rr]eversal|[Rr]everse',
            'rsi_oversold': r'[Rr][Ss][Ii].*oversold|[Oo]versold',
            'rsi_overbought': r'[Rr][Ss][Ii].*overbought|[Oo]verbought',
            'macd_cross': r'[Mm][Aa][Cc][Dd].*cross',
            'ema_bounce': r'[Ee][Mm][Aa].*bounce|[Ee][Mm][Aa].*hold',
            'consolidation_break': r'[Cc]onsolidation.*break|[Bb]reakout',
            'news_driven': r'[Nn]ews|[Ff]omc|[Nn][Ff][Pp]|[Cc][Pp][Ii]|[Pp][Mm][Ii]',
        }
        
        patterns_found = []
        for pattern_name, pattern_regex in pattern_keywords.items():
            if re.search(pattern_regex, text, re.IGNORECASE):
                patterns_found.append(pattern_name)
        
        if patterns_found:
            lesson['has_lesson'] = True
            lesson['patterns'] = patterns_found
        
        # Extract confidence level
        confidence_match = re.search(r'([Hh]igh|[Mm]edium|[Ll]ow|[Ss]trong|[Ww]eak).*confidence', text, re.IGNORECASE)
        if confidence_match:
            lesson['confidence'] = confidence_match.group(1).lower()
        
        # Extract market context
        if re.search(r'[Ll]ondon|[Ll]ondon.*session', text, re.IGNORECASE):
            lesson['context'] = lesson.get('context', []) + ['london_session']
        if re.search(r'[Nn]ew.*[Yy]ork|[Nn][Yy].*session', text, re.IGNORECASE):
            lesson['context'] = lesson.get('context', []) + ['ny_session']
        if re.search(r'[Aa]sia|[Tt]okyo.*session', text, re.IGNORECASE):
            lesson['context'] = lesson.get('context', []) + ['asia_session']
        
        return lesson
    
    def record_trade_with_lesson(self, trade_id, signal, lesson, order_ids):
        """Record a new trade with its associated lesson"""
        outcome_entry = {
            'trade_id': trade_id,
            'order_ids': order_ids,
            'symbol': signal.get('symbol'),
            'direction': signal.get('direction'),
            'entry_price': signal.get('entry_range', {}).get('mid'),
            'sl': signal.get('sl'),
            'tps': signal.get('tps'),
            'lesson': lesson,
            'opened_at': datetime.now().isoformat(),
            'status': 'OPEN',
            'result': None,
            'pnl': None,
            'exit_price': None,
            'closed_at': None
        }
        
        self.outcomes.append(outcome_entry)
        self.save()
        
        # Log the lesson learned
        if lesson.get('has_lesson'):
            lesson_log = {
                'timestamp': datetime.now().isoformat(),
                'trade_id': trade_id,
                'symbol': signal.get('symbol'),
                'lesson_type': 'NEW_TRADE',
                'patterns': lesson.get('patterns', []),
                'analysis': lesson.get('analysis', []),
                'confidence': lesson.get('confidence', 'unknown'),
                'context': lesson.get('context', [])
            }
            with open(self.lessons_file, 'a') as f:
                f.write(json.dumps(lesson_log) + '\n')
        
        return outcome_entry
    
    def record_outcome(self, trade_id, result, pnl, exit_price=None):
        """Record the outcome of a trade"""
        for outcome in self.outcomes:
            if outcome['trade_id'] == trade_id and outcome['status'] == 'OPEN':
                outcome['status'] = 'CLOSED'
                outcome['result'] = 'WIN' if pnl > 0 else 'LOSS'
                outcome['pnl'] = pnl
                outcome['exit_price'] = exit_price
                outcome['closed_at'] = datetime.now().isoformat()
                
                # Update pattern statistics
                lesson = outcome.get('lesson', {})
                patterns = lesson.get('patterns', [])
                
                for pattern in patterns:
                    if pattern not in self.patterns:
                        self.patterns[pattern] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
                    
                    if pnl > 0:
                        self.patterns[pattern]['wins'] += 1
                    else:
                        self.patterns[pattern]['losses'] += 1
                    self.patterns[pattern]['total_pnl'] += pnl
                
                self.save()
                
                # Log outcome
                outcome_log = {
                    'timestamp': datetime.now().isoformat(),
                    'trade_id': trade_id,
                    'result': outcome['result'],
                    'pnl': pnl,
                    'patterns': patterns,
                    'lesson_learned': self._generate_lesson_learned(outcome)
                }
                with open(self.lessons_file, 'a') as f:
                    f.write(json.dumps(outcome_log) + '\n')
                
                return outcome
        return None
    
    def _generate_lesson_learned(self, outcome):
        """Generate a lesson learned from the outcome"""
        lesson = outcome.get('lesson', {})
        patterns = lesson.get('patterns', [])
        result = outcome.get('result')
        
        if not patterns:
            return "No specific pattern identified"
        
        if result == 'WIN':
            return f"Patterns {patterns} resulted in a WIN. Continue using these signals."
        else:
            return f"Patterns {patterns} resulted in a LOSS. Review entry timing or SL placement."
    
    def get_pattern_stats(self):
        """Get statistics on which patterns work best"""
        stats = []
        for pattern, data in self.patterns.items():
            total = data['wins'] + data['losses']
            if total > 0:
                win_rate = (data['wins'] / total) * 100
                stats.append({
                    'pattern': pattern,
                    'total_trades': total,
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'win_rate': round(win_rate, 1),
                    'total_pnl': round(data['total_pnl'], 2)
                })
        
        return sorted(stats, key=lambda x: x['win_rate'], reverse=True)
    
    def generate_weekly_report(self):
        """Generate a weekly learning report"""
        stats = self.get_pattern_stats()
        recent_outcomes = [o for o in self.outcomes if o['status'] == 'CLOSED']
        
        # Filter to last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_outcomes = [o for o in recent_outcomes if datetime.fromisoformat(o['opened_at']) > week_ago]
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': 'Last 7 days',
            'total_trades': len(recent_outcomes),
            'wins': len([o for o in recent_outcomes if o['result'] == 'WIN']),
            'losses': len([o for o in recent_outcomes if o['result'] == 'LOSS']),
            'total_pnl': sum([o['pnl'] for o in recent_outcomes]),
            'pattern_performance': stats[:10],  # Top 10 patterns
            'best_patterns': [s for s in stats if s['win_rate'] >= 70 and s['total_trades'] >= 3],
            'avoid_patterns': [s for s in stats if s['win_rate'] <= 40 and s['total_trades'] >= 3]
        }
        
        return report


class PositionManager:
    """Manage position sizing and trade execution"""
    
    @staticmethod
    def calculate_pip_size(symbol):
        """Get pip size for symbol (price decimal places)"""
        if symbol in ['XAUUSD', 'XAGUSD']:
            return 0.01  # 2 decimal places = 1 pip
        elif symbol in ['USDJPY']:
            return 0.01  # 2 decimal places
        else:
            return 0.0001  # 4 decimal places for forex
    
    @staticmethod
    def price_diff_to_pips(price_diff, symbol):
        """Convert price difference to pips"""
        pip_size = PositionManager.calculate_pip_size(symbol)
        return price_diff / pip_size
    
    @staticmethod
    def display_trade_calculator(signal, risk_amount, executor=None):
        """
        Display OANDA-style trade calculator BEFORE executing
        Queries OANDA for ACTUAL pip value if executor provided
        Shows: 1 pip value, unit cost, max loss - like OANDA UI
        """
        symbol = signal['symbol']
        direction = signal['direction']
        sl = signal['sl']
        entry_price = signal['entry_range']['mid']
        
        # Convert symbol to OANDA format
        symbol_oanda = symbol.replace('USD', '_USD')
        if symbol_oanda == 'XAU_USD':
            symbol_oanda = 'XAU_USD'
        elif symbol_oanda == 'XAG_USD':
            symbol_oanda = 'XAG_USD'
        
        # QUERY OANDA FOR ACTUAL PIP VALUE
        if executor:
            print(f"🔍 Querying OANDA for {symbol} pip value...")
            inst_details = executor.get_instrument_details(symbol_oanda)
            if inst_details['success']:
                pip_size = inst_details['pip_size']
                pip_value_per_lot = inst_details['pip_value_sgd']
                lot_size = inst_details['lot_size']
                current_price = inst_details['current_bid']
                print(f"   ✓ OANDA pip value: ${pip_value_per_lot:.2f} SGD per {lot_size} units")
                print(f"   ✓ Current price: {current_price}")
            else:
                print(f"   ⚠️ Could not get OANDA data, using defaults")
                pip_size = PositionManager.calculate_pip_size(symbol)
                pip_value_per_lot = PIP_VALUES.get(symbol, 1.19)
                lot_size = LOT_SIZES.get(symbol, 100)
        else:
            # Fallback to hardcoded values
            pip_size = PositionManager.calculate_pip_size(symbol)
            pip_value_per_lot = PIP_VALUES.get(symbol, 1.19)
            lot_size = LOT_SIZES.get(symbol, 100)
        
        if direction == 'BUY':
            price_diff = abs(entry_price - sl)
        else:
            price_diff = abs(sl - entry_price)
        
        risk_pips = price_diff / pip_size
        
        # Calculate position
        lots = risk_amount / (pip_value_per_lot * risk_pips)
        units = int(lots * lot_size)
        units = max(1, units)
        
        # Recalculate actual risk with rounded units
        actual_risk = (units / lot_size) * pip_value_per_lot * risk_pips
        
        # Calculate 1 unit value
        unit_value_per_pip = pip_value_per_lot / lot_size
        
        # Calculate 3-tier split entries
        # Each tier risks 1/3 of total amount
        # Tier 1: High of range (33% of risk)
        # Tier 2: Mid of range (33% of risk)
        # Tier 3: Low of range (34% of risk)
        entry_high = signal['entry_range']['high']
        entry_low = signal['entry_range']['low']
        entry_mid = signal['entry_range']['mid']
        
        # Calculate position size for EACH tier (1/3 of total risk per tier)
        risk_per_tier = risk_amount / 3
        
        # Tier 1: High price, 33% risk
        tier1_units = max(1, int((risk_per_tier / (pip_value_per_lot * risk_pips)) * lot_size))
        
        # Tier 2: Mid price, 33% risk
        tier2_units = max(1, int((risk_per_tier / (pip_value_per_lot * risk_pips)) * lot_size))
        
        # Tier 3: Low price, 34% risk (remainder)
        tier3_units = max(1, int(((risk_amount - (risk_per_tier * 2)) / (pip_value_per_lot * risk_pips)) * lot_size))
        
        split_entries = [
            {'price': entry_high, 'units': tier1_units, 'tier': 1, 'risk': risk_per_tier},
            {'price': entry_mid, 'units': tier2_units, 'tier': 2, 'risk': risk_per_tier},
            {'price': entry_low, 'units': tier3_units, 'tier': 3, 'risk': risk_amount - (risk_per_tier * 2)}
        ]
        
        # Total units across all tiers
        total_units = tier1_units + tier2_units + tier3_units
        
        # Calculate actual total risk
        actual_risk_total = (total_units / lot_size) * pip_value_per_lot * risk_pips
        
        print("\n" + "="*50)
        print("📊 TRADE CALCULATOR (OANDA Live Data)")
        print("="*50)
        print(f"  Symbol:     {symbol}")
        print(f"  Direction:  {direction}")
        print(f"  Entry Range: {entry_low} - {entry_high}")
        print(f"  Stop Loss:  {sl}")
        print(f"  SL Distance: {price_diff:.2f} ({risk_pips:.0f} pips)")
        print()
        print(f"  💰 PER PIP VALUE (from OANDA):")
        print(f"     1 pip = ${pip_value_per_lot:.2f} SGD (per {lot_size} units)")
        print(f"     1 pip = ${unit_value_per_pip:.4f} SGD (per unit)")
        print()
        print(f"  📈 3-TIER SPLIT ENTRY (Each tier = 1/3 of total risk):")
        print(f"     Total Target Risk: ${risk_amount:.2f}")
        print(f"     Risk per Tier: ~${risk_per_tier:.2f}")
        print()
        for entry in split_entries:
            print(f"     Tier {entry['tier']}: {entry['units']} units @ {entry['price']} (risk: ${entry['risk']:.2f})")
        print(f"     Total Units: {total_units}")
        print()
        print(f"  ⚠️  MAX LOSS IF SL HIT (all 3 tiers):")
        print(f"     ${actual_risk_total:.2f} SGD")
        print(f"     (Target: ${risk_amount:.2f})")
        
        # Warning if actual risk differs significantly from target
        risk_diff = abs(actual_risk_total - risk_amount)
        if risk_diff > 3:
            print(f"  ⚠️  WARNING: Total risk differs by ${risk_diff:.2f}")
        
        print("="*50)
        
        return {
            'entry': entry_price,
            'units': total_units,
            'lots': lots,
            'sl': sl,
            'risk_pips': risk_pips,
            'pip_value_per_lot': pip_value_per_lot,
            'unit_value_per_pip': unit_value_per_pip,
            'expected_risk': actual_risk_total,
            'split_entries': split_entries,
            'risk_per_tier': risk_per_tier,
            'use_split': True,
            'tps': signal['tps']
        }
        # Risk = Lots × Pip_Value_per_Lot × SL_Distance_in_Pips
        # Lots = Risk ÷ (Pip_Value_per_Lot × SL_Distance)
        lots = risk_amount / (pip_value_per_lot * risk_pips)

        # Convert to units for OANDA
        units = int(lots * lot_size)

        # Minimum 1 unit
        units = max(1, units)

        return {
            'entry': entry_price,
            'units': units,
            'lots': lots,
            'sl': sl,
            'risk_pips': risk_pips,
            'pip_value_per_lot': pip_value_per_lot,
            'expected_risk': lots * pip_value_per_lot * risk_pips,
            'tps': signal['tps']
        }


class TradeMonitor:
    """Monitor open trades and manage SL/TP dynamically"""
    
    def __init__(self, executor, state, learning_db=None):
        self.executor = executor
        self.state = state
        self.learning_db = learning_db  # Learning database for outcome tracking
        self.managed_trades = {}  # Track which trades have had SL moved
        self.last_status_report = datetime.now()
        self.load_managed_trades()
    
    def load_managed_trades(self):
        """Load managed trade state"""
        if os.path.exists(OPEN_TRADES_FILE):
            with open(OPEN_TRADES_FILE) as f:
                self.managed_trades = json.load(f)
    
    def save_managed_trades(self):
        """Save managed trade state"""
        with open(OPEN_TRADES_FILE, 'w') as f:
            json.dump(self.managed_trades, f, indent=2)
    
    def alert(self, message, trade_data=None):
        """Send alert about trade action - to console, file, AND message bus for Helios"""
        print(f"🚨 {message}")
        
        # 1. Write to local alerts file
        alert = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'trade_data': trade_data or {}
        }
        with open(ALERTS_FILE, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        # 2. Write to message bus for Helios to pick up
        bus_message = {
            'from': 'quanta',
            'to': 'helios',
            'timestamp': datetime.now().isoformat(),
            'type': 'trade_alert',
            'message': message,
            'trade_data': trade_data or {}
        }
        
        bus_file = f"{BASE_DIR}/../message-bus/quanta-to-helios/pending/alert-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        os.makedirs(os.path.dirname(bus_file), exist_ok=True)
        with open(bus_file, 'w') as f:
            json.dump(bus_message, f, indent=2)
        
        # 3. Also write to CHAD_YI inbox for immediate notification
        chad_file = f"{BASE_DIR}/../message-bus/quanta-to-chad-yi/pending/alert-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        os.makedirs(os.path.dirname(chad_file), exist_ok=True)
        with open(chad_file, 'w') as f:
            json.dump(bus_message, f, indent=2)
    
    async def monitor_loop(self):
        """Main monitoring loop - runs every 5 seconds"""
        print("📊 Trade Monitor started - checking every 5 seconds")
        
        while True:
            try:
                await asyncio.sleep(5)
                await self.check_open_trades()
                await self.report_status_if_needed()
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def report_status_if_needed(self):
        """Report open trade status every 5 minutes and learning report daily"""
        now = datetime.now()
        if (now - self.last_status_report).seconds >= 300:  # 5 minutes
            await self.report_open_trades_status()
            
            # Also generate learning report if we have learning db
            if self.learning_db and now.hour == 20 and now.minute < 10:  # 8 PM daily
                await self.report_learning_status()
            
            self.last_status_report = now
    
    async def report_learning_status(self):
        """Report learning/performance insights"""
        report = self.learning_db.generate_weekly_report()
        
        lines = [
            "🧠 WEEKLY LEARNING REPORT",
            f"Period: {report['period']}",
            f"Total Trades: {report['total_trades']} | Wins: {report['wins']} | Losses: {report['losses']}",
            f"Total P&L: ${report['total_pnl']:+.2f}",
            ""
        ]
        
        if report['best_patterns']:
            lines.append("✅ BEST PATTERNS (70%+ win rate):")
            for p in report['best_patterns']:
                lines.append(f"   • {p['pattern']}: {p['win_rate']}% ({p['wins']}W/{p['losses']}L) | P&L: ${p['total_pnl']:+.2f}")
            lines.append("")
        
        if report['avoid_patterns']:
            lines.append("⚠️ AVOID PATTERNS (40%- win rate):")
            for p in report['avoid_patterns']:
                lines.append(f"   • {p['pattern']}: {p['win_rate']}% ({p['wins']}W/{p['losses']}L) | P&L: ${p['total_pnl']:+.2f}")
            lines.append("")
        
        if report['pattern_performance']:
            lines.append("📊 ALL PATTERNS:")
            for p in report['pattern_performance'][:5]:
                lines.append(f"   • {p['pattern']}: {p['win_rate']}% ({p['total_trades']} trades)")
        
        report_msg = "\n".join(lines)
        self.alert(report_msg, trade_data={'type': 'learning_report', 'report': report})
    
    async def report_open_trades_status(self):
        """Report status of all open trades to CHAD_YI"""
        result = self.executor.get_open_trades()
        
        if not result['success']:
            return
        
        trades = result.get('trades', [])
        
        if not trades:
            return  # No open trades, no report needed
        
        # Build status report
        status_lines = ["📊 ONGOING TRADES STATUS:"]
        total_pnl = 0
        
        for trade in trades:
            trade_id = trade['id']
            symbol = trade['instrument'].replace('_', '')
            direction = 'BUY' if int(trade['currentUnits']) > 0 else 'SELL'
            entry = float(trade['price'])
            units = abs(int(trade['currentUnits']))
            
            # Get current price and PnL
            price_result = self.executor.get_price(trade['instrument'])
            if price_result['success']:
                if direction == 'BUY':
                    current = price_result['bid']
                else:
                    current = price_result['ask']
                
                pip_size = 0.01 if symbol in ['XAUUSD', 'XAGUSD', 'USDJPY'] else 0.0001
                if direction == 'BUY':
                    pips = (current - entry) / pip_size
                else:
                    pips = (entry - current) / pip_size
                
                unrealized_pnl = trade.get('unrealizedPL', 0)
                total_pnl += float(unrealized_pnl)
                
                # Get current SL status
                sl_status = "Initial"
                managed = self.managed_trades.get(trade_id, {})
                if managed.get('trailing_active'):
                    sl_status = "🔒 Trailing"
                elif managed.get('profit_locked'):
                    sl_status = "🔒 +20p Locked"
                elif managed.get('breakeven_moved'):
                    sl_status = "🔒 Breakeven"
                
                status_lines.append(f"  • {symbol} {direction} | Entry: {entry} | Current: {current:.2f} | Pips: {pips:+.1f} | P&L: ${float(unrealized_pnl):+.2f} | SL: {sl_status}")
        
        status_lines.append(f"\n💰 TOTAL UNREALIZED P&L: ${total_pnl:+.2f}")
        
        # Send consolidated report
        report_message = "\n".join(status_lines)
        self.alert(report_message, trade_data={'open_trades_count': len(trades), 'total_unrealized_pnl': total_pnl})
    
    async def check_open_trades(self):
        """Check all open trades and manage SL"""
        result = self.executor.get_open_trades()
        
        if not result['success']:
            return
        
        trades = result.get('trades', [])
        current_trade_ids = {t['id'] for t in trades}
        
        # Check for closed trades (were in managed_trades but not in current open trades)
        for trade_id in list(self.managed_trades.keys()):
            if trade_id not in current_trade_ids:
                await self.report_closed_trade(trade_id)
        
        for trade in trades:
            await self.manage_trade(trade)
    
    async def report_closed_trade(self, trade_id):
        """Report trade closure - profit or loss"""
        managed = self.managed_trades.get(trade_id, {})
        symbol = managed.get('symbol', 'UNKNOWN')
        direction = managed.get('direction', 'UNKNOWN')
        entry = managed.get('entry', 0)
        
        # Import BASE_URL from oanda_executor
        from oanda_executor import BASE_URL
        
        # Get trade history from OANDA to find realized PnL
        try:
            # Trade is closed, get from transactions
            trans_url = f'{BASE_URL}/accounts/{self.executor.account_id}/transactions'
            trans_params = {'type': 'ORDER_FILL', 'count': 50}
            trans_response = requests.get(trans_url, headers=self.executor.headers, params=trans_params)
            
            if trans_response.status_code == 200:
                transactions = trans_response.json().get('transactions', [])
                for tx in transactions:
                    if tx.get('tradeClosed') and tx['tradeClosed'].get('tradeID') == trade_id:
                        realized_pl = float(tx['tradeClosed'].get('realizedPL', 0))
                        
                        if realized_pl > 0:
                            self.alert(
                                f"💰 PROFIT TAKEN: {symbol} {direction} closed at +${realized_pl:.2f}",
                                trade_data={'trade_id': trade_id, 'symbol': symbol, 'pnl': realized_pl, 'status': 'PROFIT'}
                            )
                        else:
                            self.alert(
                                f"❌ LOSS: {symbol} {direction} closed at ${realized_pl:.2f}",
                                trade_data={'trade_id': trade_id, 'symbol': symbol, 'pnl': realized_pl, 'status': 'LOSS'}
                            )
                        
                        # Record outcome in learning database
                        if self.learning_db:
                            self.learning_db.record_outcome(trade_id, 'WIN' if realized_pl > 0 else 'LOSS', realized_pl)
                        
                        # Update state
                        self.state.update_balance(realized_pl)
                        break
        except Exception as e:
            print(f"⚠️ Error reporting closed trade {trade_id}: {e}")
        
        # Remove from managed trades
        if trade_id in self.managed_trades:
            del self.managed_trades[trade_id]
            self.save_managed_trades()
    
    async def manage_trade(self, trade):
        """Manage a single trade's SL/TP"""
        trade_id = trade['id']
        symbol = trade['instrument']  # XAU_USD format
        direction = 'BUY' if int(trade['currentUnits']) > 0 else 'SELL'
        entry = float(trade['price'])
        
        # Get current price
        price_result = self.executor.get_price(symbol)
        if not price_result['success']:
            return
        
        if direction == 'BUY':
            current_price = price_result['bid']  # Use bid for SELL to close
        else:
            current_price = price_result['ask']  # Use ask for BUY to close
        
        # Calculate pips in profit
        symbol_clean = symbol.replace('_', '')
        pip_size = 0.01 if symbol_clean in ['XAUUSD', 'XAGUSD', 'USDJPY'] else 0.0001
        pip_value = PIP_VALUES.get(symbol_clean, 0.01)
        
        if direction == 'BUY':
            price_diff = current_price - entry
        else:
            price_diff = entry - current_price
        
        pips_profit = price_diff / pip_size
        
        # Get current SL
        current_sl = None
        if trade.get('stopLossOrder'):
            current_sl = float(trade['stopLossOrder']['price'])
        
        # Initialize trade tracking
        if trade_id not in self.managed_trades:
            self.managed_trades[trade_id] = {
                'entry': entry,
                'direction': direction,
                'symbol': symbol,
                'breakeven_moved': False,
                'profit_locked': False,
                'trailing_active': False
            }
        
        managed = self.managed_trades[trade_id]
        
        # RULE 1: +20 pips → Move SL to breakeven
        if pips_profit >= 20 and not managed['breakeven_moved']:
            result = self.executor.modify_sl(trade_id, entry)
            if result['success']:
                managed['breakeven_moved'] = True
                self.save_managed_trades()
                self.alert(
                    f"Trade {trade_id}: SL moved to BREAKEVEN (+{pips_profit:.1f} pips)",
                    trade_data={'trade_id': trade_id, 'action': 'sl_to_breakeven', 'pips_profit': pips_profit, 'new_sl': entry}
                )
        
        # RULE 2: +50 pips → Move SL to +20 pips profit
        elif pips_profit >= 50 and not managed['profit_locked']:
            if direction == 'BUY':
                new_sl = entry + (20 * pip_size)  # +20 pips in price terms
            else:
                new_sl = entry - (20 * pip_size)
            
            result = self.executor.modify_sl(trade_id, new_sl)
            if result['success']:
                managed['profit_locked'] = True
                self.save_managed_trades()
                self.alert(
                    f"Trade {trade_id}: SL locked at +20 pips profit ({new_sl:.2f})",
                    trade_data={'trade_id': trade_id, 'action': 'sl_lock_profit', 'pips_profit': pips_profit, 'new_sl': new_sl}
                )
        
        # RULE 3: +100 pips → Trail SL at -50 pips from current
        elif pips_profit >= 100:
            if direction == 'BUY':
                new_sl = current_price - (50 * pip_size)  # -50 pips from current
                # Only move if new SL is better
                if current_sl is None or new_sl > current_sl:
                    result = self.executor.modify_sl(trade_id, new_sl)
                    if result['success']:
                        managed['trailing_active'] = True
                        self.save_managed_trades()
                        self.alert(
                            f"Trade {trade_id}: Trailing SL at -50 pips ({new_sl:.2f})",
                            trade_data={'trade_id': trade_id, 'action': 'sl_trailing', 'pips_profit': pips_profit, 'new_sl': new_sl}
                        )
            else:
                new_sl = current_price + (50 * pip_size)
                if current_sl is None or new_sl < current_sl:
                    result = self.executor.modify_sl(trade_id, new_sl)
                    if result['success']:
                        managed['trailing_active'] = True
                        self.save_managed_trades()
                        self.alert(
                            f"Trade {trade_id}: Trailing SL at -50 pips ({new_sl:.2f})",
                            trade_data={'trade_id': trade_id, 'action': 'sl_trailing', 'pips_profit': pips_profit, 'new_sl': new_sl}
                        )


def rotate_logs():
    """Clean up old logs"""
    try:
        now = datetime.now()
        cutoff = now - timedelta(days=MAX_LOG_DAYS)
        
        for log_file in glob.glob(f'{LOG_DIR}/*.jsonl') + glob.glob(f'{INBOX_DIR}/*.jsonl'):
            stat = os.stat(log_file)
            if datetime.fromtimestamp(stat.st_mtime) < cutoff:
                os.remove(log_file)
                print(f"🗑️ Rotated: {os.path.basename(log_file)}")
    except Exception as e:
        print(f"⚠️ Log rotation error: {e}")


async def find_callistofx_channel():
    """Find the CallistoFx channel"""
    print("🔍 Searching for CallistoFx Premium channel...")
    
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if "callistofx" in name.lower() and "premium" in name.lower():
            print(f"✅ Found: {name} (ID: {dialog.id})")
            return dialog.id
    
    print("❌ Channel not found")
    return None


async def main():
    """Main entry point"""
    print("🚀 Quanta v4.0 - With Live Trade Management & Learning")
    print("=" * 50)
    
    # Initialize
    rotate_logs()
    state = TradingState()
    parser = SignalParser()
    position_mgr = PositionManager()
    learning_db = LearningDatabase()  # Initialize learning system
    
    # Initialize OANDA executor
    executor = OandaExecutor()
    connection_test = executor.test_connection()
    
    if connection_test['success']:
        print(f"✅ OANDA Connected: {connection_test['account']}")
        print(f"💰 Balance: ${connection_test['balance']} {connection_test['currency']}")
    else:
        print(f"❌ OANDA Connection Failed: {connection_test.get('error')}")
        return
    
    print(f"📊 Daily Risk Used: {state.daily_stats['risk_used_percent']}%")
    print(f"📈 Trades Today: {state.daily_stats['trades_taken']}")
    print(f"🧠 Learning Database: {len(learning_db.outcomes)} trades recorded")
    print()
    
    # Start trade monitor (pass learning_db for outcome tracking)
    monitor = TradeMonitor(executor, state, learning_db)
    monitor_task = asyncio.create_task(monitor.monitor_loop())
    
    # Connect to Telegram
    await client.start(phone=lambda: PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Telegram logged in as: {me.first_name}")
    
    # Find channel
    channel_id = await find_callistofx_channel()
    if not channel_id:
        return
    
    print(f"🎯 Monitoring CallistoFX for signals...")
    print(f"🧠 Learning Mode: Extracting lessons from every message")
    print(f"⚙️  Trade Management:")
    print(f"   • +20 pips → SL to breakeven")
    print(f"   • +50 pips → Lock +20 pips profit")
    print(f"   • +100 pips → Trail SL at -50 pips")
    print()
    
    # Message handler
    @client.on(events.NewMessage(chats=channel_id))
    async def handle_message(event):
        text = event.message.text
        if not text:
            return
        
        # Parse signal
        signal = parser.parse_signal(text)
        
        # ALWAYS parse for lessons (learning from every message)
        lesson = learning_db.parse_lesson(text)
        
        if lesson.get('has_lesson') and not signal:
            # Educational message without trade signal
            print(f"\n📚 LESSON LEARNED:")
            if lesson.get('patterns'):
                print(f"   Patterns: {', '.join(lesson['patterns'])}")
            if lesson.get('analysis'):
                print(f"   Analysis: {lesson['analysis'][0][:100]}...")
            # Save lesson
            lesson_log = {
                'timestamp': datetime.now().isoformat(),
                'lesson_type': 'EDUCATIONAL',
                'patterns': lesson.get('patterns', []),
                'analysis': lesson.get('analysis', []),
                'confidence': lesson.get('confidence'),
                'context': lesson.get('context', [])
            }
            with open(LEARNING_DB_FILE.replace('.json', '_lessons.jsonl'), 'a') as f:
                f.write(json.dumps(lesson_log) + '\n')
        
        if not signal:
            print(f"💬 Message: {text[:50]}...")
            return
        
        print(f"\n🚨 SIGNAL: {signal['symbol']} {signal['direction']}")
        print(f"   Range: {signal['entry_range']['low']} - {signal['entry_range']['high']}")
        print(f"   SL: {signal['sl']} | TPs: {signal['tps']}")
        
        # Show lesson if available
        if lesson.get('has_lesson'):
            print(f"\n📚 LESSON:")
            if lesson.get('patterns'):
                print(f"   Patterns: {', '.join(lesson['patterns'])}")
            if lesson.get('analysis'):
                print(f"   Why: {lesson['analysis'][0][:80]}...")
        
        # Calculate score
        score = parser.calculate_signal_score(signal, {})
        print(f"   Score: {score}/100")
        
        if score < 40:
            print(f"   ❌ SKIPPED: Score too low")
            return
        
        if not state.can_trade():
            print(f"   ❌ SKIPPED: Risk limits")
            return
        
        # Display OANDA-style trade calculator BEFORE executing
        # Pass executor to query OANDA's ACTUAL pip value
        risk_amount = state.calculate_risk_amount()  # $20 fixed
        position = position_mgr.display_trade_calculator(signal, risk_amount, executor=executor)
        
        if not position:
            print(f"   ❌ Position calc failed")
            return
        
        # Execute 3-tier split entry via OANDA
        symbol_oanda = signal['symbol'].replace('USD', '_USD')
        if symbol_oanda == 'XAU_USD':
            symbol_oanda = 'XAU_USD'
        elif symbol_oanda == 'XAG_USD':
            symbol_oanda = 'XAG_USD'
        
        # Execute 3-tier split entry via OANDA
        symbol_oanda = signal['symbol'].replace('USD', '_USD')
        if symbol_oanda == 'XAU_USD':
            symbol_oanda = 'XAU_USD'
        elif symbol_oanda == 'XAG_USD':
            symbol_oanda = 'XAG_USD'
        
        # Place 3 separate limit orders for split entry
        all_success = True
        order_ids = []
        
        print(f"\n🚀 Executing 3-Tier Split Entry...")
        
        for entry in position['split_entries']:
            if entry['units'] <= 0:
                continue
                
            # Create LIMIT order at specific price (not market)
            order_result = executor.create_limit_order(
                instrument=symbol_oanda,
                direction=signal['direction'],
                units=entry['units'],
                price=entry['price'],
                stop_loss=position['sl'],
                take_profit=position['tps'][0]
            )
            
            if order_result['success']:
                order_ids.append(order_result['order_id'])
                print(f"   ✅ Tier {entry['tier']}: {entry['units']} units @ {entry['price']} (risk: ${entry.get('risk', 0):.2f})")
            else:
                print(f"   ❌ Tier {entry['tier']} failed: {order_result.get('error')}")
                all_success = False
        
        if all_success and order_ids:
            # Record as single trade with multiple entries
            trade = {
                'id': ','.join(order_ids),
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry': position['entry'],
                'units': position['units'],
                'sl': position['sl'],
                'tp1': position['tps'][0],
                'split_entries': position['split_entries'],
                'status': 'OPEN',
                'opened_at': datetime.now().isoformat()
            }
            state.record_trade(trade)
            
            # Record in learning database with lesson
            if learning_db:
                learning_db.record_trade_with_lesson(','.join(order_ids), signal, lesson, order_ids)
            
            # Report to Helios and CHAD_YI via message bus
            trade_alert_data = {
                'trade_id': ','.join(order_ids),
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry': position['entry'],
                'units': position['units'],
                'sl': position['sl'],
                'tp': position['tps'][0],
                'risk': state.calculate_risk_amount(),
                'split_entries': position['split_entries'],
                'lesson': lesson if lesson.get('has_lesson') else None
            }
            monitor.alert(
                f"✅ 3-TIER SPLIT ENTRY: {signal['symbol']} {signal['direction']} - {len(order_ids)} orders placed",
                trade_data=trade_alert_data
            )
        else:
            print(f"   ⚠️ Some tiers failed - check OANDA")
            monitor.alert(
                f"⚠️ PARTIAL FILL: {signal['symbol']} - Only {len(order_ids)}/3 tiers executed",
                trade_data={'symbol': signal['symbol'], 'order_ids': order_ids}
            )
    
    # Run both tasks
    await asyncio.gather(
        monitor_task,
        client.run_until_disconnected()
    )


if __name__ == '__main__':
    async def start():
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ Telegram not authorized - run interactive setup first")
            return
        await main()
    
    client.loop.run_until_complete(start())
