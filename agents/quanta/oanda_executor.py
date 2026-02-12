#!/usr/bin/env python3
"""
Quanta OANDA Trade Execution Module
Handles position sizing, multiple TPs, risk management
"""

import json
from datetime import datetime
import oandapyV20
from oandapyV20 import endpoints
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails
import logging

from trading_config import (
    MAX_RISK_PER_TRADE, ACCOUNT_BALANCE, OANDA_ACCOUNT_ID,
    OANDA_ACCESS_TOKEN, OANDA_ENVIRONMENT, PAPER_TRADING_MODE,
    SPLIT_POSITIONS, PARTIAL_CLOSE_AT_TP1
)

# OANDA API Setup
if PAPER_TRADING_MODE:
    OANDA_ENV = "practice"
else:
    OANDA_ENV = "live"

# Initialize OANDA API
api = oandapyV20.API(
    access_token=OANDA_ACCESS_TOKEN,
    environment=OANDA_ENV
)

# Pip values for different pairs
PIP_VALUES = {
    'XAUUSD': 0.01,   # Gold - 1 pip = $0.01
    'XAGUSD': 0.001,  # Silver
    'EURUSD': 0.0001,
    'GBPUSD': 0.0001,
    'USDJPY': 0.01,
}

def calculate_position_size(signal):
    """
    Calculate position size based on $20 max risk
    
    Formula: Position Size = Risk Amount / (Stop Loss Distance in pips * Pip Value)
    """
    pair = signal.get('pair', 'XAUUSD')
    entry = signal.get('entry')
    stop_loss = signal.get('stop_loss')
    
    if not entry or not stop_loss:
        print(f"❌ Cannot calculate position size - missing entry or SL")
        return None
    
    # Calculate risk in pips
    if signal['action'] == 'BUY':
        risk_pips = abs(entry - stop_loss)
    else:  # SELL
        risk_pips = abs(stop_loss - entry)
    
    # Get pip value for pair
    pip_value = PIP_VALUES.get(pair, 0.01)  # Default to gold
    
    # Calculate position size
    # For XAUUSD: $20 risk / (5 pips * $0.01/pip) = 0.04 lots = 400 units
    risk_amount = MAX_RISK_PER_TRADE
    
    if pair in ['XAUUSD', 'XAGUSD']:
        # For gold/silver: position size in units
        # 1 unit = $0.01 per pip for XAUUSD
        position_size_units = risk_amount / (risk_pips * pip_value)
        position_size_lots = position_size_units / 100  # Convert to lots (1 lot = 100 units for gold)
    else:
        # For forex
        position_size_units = risk_amount / (risk_pips * pip_value)
        position_size_lots = position_size_units / 100000  # 1 standard lot = 100,000 units
    
    # Round to 2 decimal places for micro lots
    position_size_lots = round(position_size_lots, 2)
    
    # Minimum 0.01 lots (micro lot)
    if position_size_lots < 0.01:
        position_size_lots = 0.01
    
    print(f"📊 Position Sizing:")
    print(f"   Risk: ${risk_amount}")
    print(f"   SL Distance: {risk_pips} pips")
    print(f"   Position Size: {position_size_lots} lots ({int(position_size_lots * 100)} units)")
    
    return {
        'lots': position_size_lots,
        'units': int(position_size_lots * 100) if pair in ['XAUUSD', 'XAGUSD'] else int(position_size_lots * 100000),
        'risk_pips': risk_pips,
        'pip_value': pip_value
    }

def split_position_for_multiple_tps(signal, position_size):
    """
    Split position into 3 parts for 3 TPs:
    - Position 1: 1/3 size, TP at TP1
    - Position 2: 1/3 size, TP at TP2
    - Position 3: 1/3 size, TP at TP3 (runner)
    """
    take_profits = signal.get('take_profits', [])
    
    if len(take_profits) < 2:
        # Single TP - don't split
        return [{
            'size': position_size['units'],
            'tp': take_profits[0] if take_profits else signal.get('take_profit'),
            'label': 'Full Position'
        }]
    
    positions = []
    base_size = position_size['units'] // 3
    
    # Position 1 - Close at TP1
    positions.append({
        'size': base_size,
        'tp': take_profits[0],
        'label': 'TP1 (1/3)',
        'partial_close': True
    })
    
    # Position 2 - Close at TP2
    if len(take_profits) >= 2:
        positions.append({
            'size': base_size,
            'tp': take_profits[1],
            'label': 'TP2 (1/3)',
            'partial_close': True
        })
    
    # Position 3 - Runner to TP3 (or keep running)
    remaining = position_size['units'] - (base_size * 2)
    tp3 = take_profits[2] if len(take_profits) >= 3 else take_profits[-1]
    positions.append({
        'size': remaining,
        'tp': tp3,
        'label': 'TP3 Runner',
        'trailing_stop': True
    })
    
    print(f"📦 Split into {len(positions)} positions:")
    for i, pos in enumerate(positions, 1):
        print(f"   Position {i}: {pos['size']} units, TP: {pos['tp']}, {pos['label']}")
    
    return positions

def execute_trade(signal):
    """
    Execute trade on OANDA with proper risk management
    """
    if PAPER_TRADING_MODE:
        print(f"\n🧪 PAPER TRADING MODE - Simulating trade execution:")
    else:
        print(f"\n💰 LIVE TRADING - Executing real trade:")
    
    # Calculate position size
    position_size = calculate_position_size(signal)
    if not position_size:
        return None
    
    # Split for multiple TPs
    positions = split_position_for_multiple_tps(signal, position_size)
    
    results = []
    
    for i, pos in enumerate(positions, 1):
        print(f"\n📤 Executing Position {i}/{len(positions)}...")
        
        if PAPER_TRADING_MODE:
            # Simulate the trade
            result = simulate_trade(signal, pos, i)
            results.append(result)
        else:
            # Real OANDA execution
            try:
                result = execute_oanda_order(signal, pos, i)
                results.append(result)
            except Exception as e:
                print(f"❌ Trade execution failed: {e}")
                return None
    
    # Save trade record
    trade_record = {
        'timestamp': datetime.now().isoformat(),
        'signal': signal,
        'positions': positions,
        'results': results,
        'total_units': sum(p['units'] for p in positions),
        'risk_usd': MAX_RISK_PER_TRADE,
        'mode': 'paper' if PAPER_TRADING_MODE else 'live'
    }
    
    with open('/home/chad-yi/.openclaw/workspace/agents/quanta/inbox/executed_trades.jsonl', 'a') as f:
        f.write(json.dumps(trade_record) + '\n')
    
    print(f"\n✅ Trade execution complete!")
    print(f"   Total positions: {len(positions)}")
    print(f"   Total units: {trade_record['total_units']}")
    print(f"   Risk: ${MAX_RISK_PER_TRADE}")
    
    return trade_record

def simulate_trade(signal, position, index):
    """Simulate a trade for paper trading"""
    result = {
        'position_id': f"PAPER_{datetime.now().strftime('%H%M%S')}_{index}",
        'units': position['size'],
        'entry': signal['entry'],
        'stop_loss': signal.get('stop_loss'),
        'take_profit': position['tp'],
        'status': 'OPEN',
        'label': position['label']
    }
    
    print(f"   🧪 SIMULATED: {position['size']} units @ {signal['entry']}")
    print(f"      SL: {signal.get('stop_loss')} | TP: {position['tp']}")
    
    return result

def execute_oanda_order(signal, position, index):
    """Execute real order on OANDA"""
    # This would use actual OANDA API
    # For now, return placeholder
    print(f"   💰 REAL ORDER would be placed here")
    print(f"      Pair: {signal['pair']}")
    print(f"      Units: {position['size']}")
    print(f"      Entry: {signal['entry']}")
    print(f"      SL: {signal.get('stop_loss')}")
    print(f"      TP: {position['tp']}")
    
    # TODO: Implement actual OANDA API call
    # order = MarketOrderRequest(...)
    # rv = api.request(order)
    
    return {
        'position_id': f"PENDING_IMPLEMENTATION",
        'status': 'NOT_IMPLEMENTED'
    }

if __name__ == '__main__':
    # Test with sample signal
    test_signal = {
        'action': 'BUY',
        'pair': 'XAUUSD',
        'entry': 2030.50,
        'stop_loss': 2025.50,
        'take_profit': 2040.50,
        'take_profits': [2035.00, 2040.50, 2045.00],
        'rr_ratio': 2.0
    }
    
    print("=" * 50)
    print("TESTING TRADE EXECUTION")
    print("=" * 50)
    result = execute_trade(test_signal)
    print("\nResult:", json.dumps(result, indent=2, default=str))
