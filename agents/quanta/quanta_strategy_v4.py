#!/usr/bin/env python3
"""
Quanta v4.0 - CORRECTED Strategy
$20 fixed risk, 3-tier entry, 5 TPs, runner with trailing SL
"""

import json
import os
from datetime import datetime
import re

# Trading Configuration
RISK_PER_TRADE = 20  # $20 fixed for first 20 trades
ACCOUNT_BALANCE = 10000  # Will update from OANDA

# Exit Rules
EXIT_SPLITS = [
    (20, 0.10),   # +20 pips: 10%
    (40, 0.10),   # +40 pips: 10%
    (60, 0.10),   # +60 pips: 10%
    (80, 0.10),   # +80 pips: 10%
    (100, 0.10),  # +100 pips: 10%
]
# After TP5: 50% runner remains

# Stop Loss Rules
SL_TO_BE_AT = 20  # +20 pips: move to breakeven
TRAIL_START_AT = 100  # +100 pips: start trailing
TRAIL_DISTANCE = 100  # 100 pips behind price

# Runner Rules
RUNNER_CLOSE_PCT = 0.10  # Close 10% of remaining every +50 pips
RUNNER_INTERVAL = 50  # Every +50 pips beyond +100

class TradingState:
    """Manage trading state and position tracking"""
    
    def __init__(self):
        self.balance = ACCOUNT_BALANCE
        self.risk_amount = RISK_PER_TRADE
        self.open_trades = []
        self.trade_history = []
    
    def calculate_position_size(self, entry, sl, symbol='XAUUSD'):
        """
        Calculate position size based on $20 fixed risk
        
        Example:
        - Entry: 2682.5
        - SL: 2675
        - Risk pips: 7.5
        - Risk $: $20
        - Size: 0.267 lots (for XAUUSD)
        """
        risk_pips = abs(entry - sl)
        
        if risk_pips <= 0:
            return None
        
        # XAUUSD: $0.01 per pip per unit
        # $20 risk ÷ 7.5 pips = $2.67 per pip needed
        # $2.67 ÷ $0.01 = 267 units = 0.267 lots
        pip_value = 0.01  # XAUUSD
        units_needed = self.risk_amount / (risk_pips * pip_value)
        lots = units_needed / 100  # Convert to lots
        
        return {
            'total_lots': round(lots, 3),
            'total_units': int(units_needed),
            'risk_pips': risk_pips,
            'risk_amount': self.risk_amount
        }
    
    def calculate_3tier_entry(self, range_high, range_low, total_lots):
        """
        Split entry into 3 tiers (33%/33%/34%)
        
        Example range 2680-2685:
        - Tier 1 (33%): 2685.0 (high)
        - Tier 2 (33%): 2682.5 (mid)
        - Tier 3 (34%): 2680.0 (low)
        """
        range_mid = (range_high + range_low) / 2
        
        return [
            {'tier': 1, 'price': range_high, 'lots': round(total_lots * 0.33, 3)},
            {'tier': 2, 'price': range_mid, 'lots': round(total_lots * 0.33, 3)},
            {'tier': 3, 'price': range_low, 'lots': round(total_lots * 0.34, 3)},
        ]
    
    def execute_trade(self, signal):
        """
        Execute trade with full strategy
        
        Returns trade object with all details
        """
        symbol = signal['symbol']
        direction = signal['direction']
        range_high = signal['entry_range']['high']
        range_low = signal['entry_range']['low']
        sl = signal['sl']
        
        # Calculate position size
        entry_mid = (range_high + range_low) / 2
        position = self.calculate_position_size(entry_mid, sl, symbol)
        
        if not position:
            return None
        
        # Calculate 3-tier entry
        tiers = self.calculate_3tier_entry(range_high, range_low, position['total_lots'])
        
        # Build trade object
        trade = {
            'id': f"{symbol}-{direction}-{datetime.now().strftime('%H%M%S')}",
            'symbol': symbol,
            'direction': direction,
            'entry_range': {'high': range_high, 'low': range_low, 'mid': entry_mid},
            'sl': sl,
            'tiers': tiers,
            'total_lots': position['total_lots'],
            'risk_amount': position['risk_amount'],
            'status': 'OPEN',
            'opened_at': datetime.now().isoformat(),
            
            # Track exits
            'exits_completed': [],
            'lots_remaining': position['total_lots'],
            'current_sl': sl,
            'sl_moved_to_be': False,
            
            # Runner tracking
            'runner_active': False,
            'runner_lots': 0,
            'runner_next_close_at': None,
        }
        
        return trade
    
    def update_trade_on_price_move(self, trade, current_price):
        """
        Update trade as price moves
        
        Called on every price tick to check:
        - SL moves
        - TP hits
        - Runner management
        """
        if trade['status'] != 'OPEN':
            return None
        
        direction = trade['direction']
        entry_mid = trade['entry_range']['mid']
        
        # Calculate pips in profit
        if direction == 'BUY':
            pips_profit = current_price - entry_mid
            sl_hit = current_price <= trade['current_sl']
        else:  # SELL
            pips_profit = entry_mid - current_price
            sl_hit = current_price >= trade['current_sl']
        
        # Check if SL hit
        if sl_hit:
            return {'action': 'CLOSE_ALL', 'reason': 'SL_HIT'}
        
        updates = []
        
        # Check +20 pips: Move SL to BE
        if pips_profit >= 20 and not trade['sl_moved_to_be']:
            trade['current_sl'] = entry_mid  # Move to breakeven
            trade['sl_moved_to_be'] = True
            updates.append({'action': 'MOVE_SL_BE', 'pips': pips_profit})
        
        # Check standard TPs (+20, +40, +60, +80, +100)
        for tp_pips, close_pct in EXIT_SPLITS:
            if pips_profit >= tp_pips:
                # Check if this TP already done
                already_done = any(e['pips'] == tp_pips for e in trade['exits_completed'])
                
                if not already_done:
                    lots_to_close = trade['total_lots'] * close_pct
                    trade['lots_remaining'] -= lots_to_close
                    trade['exits_completed'].append({
                        'pips': tp_pips,
                        'lots': lots_to_close,
                        'pct': close_pct,
                        'price': current_price
                    })
                    updates.append({
                        'action': 'CLOSE_PARTIAL',
                        'pips': tp_pips,
                        'lots': lots_to_close,
                        'remaining': trade['lots_remaining']
                    })
        
        # Check runner activation (+100 pips)
        if pips_profit >= 100 and not trade['runner_active']:
            trade['runner_active'] = True
            trade['runner_lots'] = trade['lots_remaining']  # Should be 50%
            trade['runner_next_close_at'] = 150  # Next close at +150
            updates.append({
                'action': 'RUNNER_ACTIVATED',
                'lots': trade['runner_lots']
            })
        
        # Runner management (+150, +200, +250, ...)
        if trade['runner_active']:
            next_close = trade['runner_next_close_at']
            
            while pips_profit >= next_close and trade['runner_lots'] > 0:
                # Close 10% of whatever is LEFT
                close_lots = trade['runner_lots'] * RUNNER_CLOSE_PCT
                
                if close_lots < 0.01:  # Minimum lot size
                    break
                
                trade['runner_lots'] -= close_lots
                trade['lots_remaining'] -= close_lots
                
                # Move SL up 100 pips behind
                if direction == 'BUY':
                    new_sl = current_price - TRAIL_DISTANCE
                else:
                    new_sl = current_price + TRAIL_DISTANCE
                
                trade['current_sl'] = max(trade['current_sl'], new_sl)  # Only move in favorable direction
                
                updates.append({
                    'action': 'RUNNER_CLOSE',
                    'pips': next_close,
                    'lots': close_lots,
                    'remaining': trade['runner_lots'],
                    'new_sl': trade['current_sl']
                })
                
                next_close += RUNNER_INTERVAL
            
            trade['runner_next_close_at'] = next_close
            
            # If runner fully closed
            if trade['runner_lots'] <= 0.01:
                trade['status'] = 'CLOSED'
                updates.append({'action': 'TRADE_COMPLETE', 'reason': 'RUNNER_FULLY_CLOSED'})
        
        return updates if updates else None
    
    def close_trade(self, trade, reason):
        """Close trade and record in history"""
        trade['status'] = 'CLOSED'
        trade['closed_at'] = datetime.now().isoformat()
        trade['close_reason'] = reason
        
        # Calculate P&L (simplified)
        # In real implementation, calculate from actual prices
        
        self.trade_history.append(trade)
        self.open_trades.remove(trade)
        
        return trade


# Test the strategy
if __name__ == "__main__":
    state = TradingState()
    
    # Test signal
    signal = {
        'symbol': 'XAUUSD',
        'direction': 'BUY',
        'entry_range': {'high': 2685.0, 'low': 2680.0},
        'sl': 2675.0
    }
    
    print("=" * 60)
    print("QUANTA v4.0 - STRATEGY TEST")
    print("=" * 60)
    
    # Execute trade
    trade = state.execute_trade(signal)
    
    print(f"\nTrade ID: {trade['id']}")
    print(f"Symbol: {trade['symbol']} {trade['direction']}")
    print(f"Entry Range: {trade['entry_range']['low']} - {trade['entry_range']['high']}")
    print(f"SL: {trade['sl']}")
    print(f"Total Lots: {trade['total_lots']}")
    print(f"Risk: ${trade['risk_amount']}")
    
    print(f"\n3-Tier Entry:")
    for tier in trade['tiers']:
        print(f"  Tier {tier['tier']}: {tier['lots']} lots @ {tier['price']}")
    
    # Simulate price movement
    print(f"\nSimulating Price Movement:")
    
    test_prices = [
        2682,   # Just entered
        2700,   # +17.5 pips (almost at BE move)
        2705,   # +22.5 pips (BE move done)
        2720,   # +37.5 pips (TP1 done)
        2740,   # +57.5 pips (TP2 done)
        2760,   # +77.5 pips (TP3 done)
        2780,   # +97.5 pips (TP4 done)
        2800,   # +117.5 pips (TP5 done, runner active)
        2850,   # +167.5 pips (runner close 1)
        2900,   # +217.5 pips (runner close 2)
    ]
    
    for price in test_prices:
        updates = state.update_trade_on_price_move(trade, price)
        if updates:
            for update in updates:
                print(f"  Price {price}: {update['action']}")
                if 'pips' in update:
                    print(f"    Pips: {update['pips']}")
                if 'remaining' in update:
                    print(f"    Remaining: {update['remaining']:.3f} lots")
                if 'new_sl' in update:
                    print(f"    New SL: {update['new_sl']}")
    
    print(f"\nFinal State:")
    print(f"  Lots Remaining: {trade['lots_remaining']:.3f}")
    print(f"  Runner Active: {trade['runner_active']}")
    print(f"  Current SL: {trade['current_sl']}")
