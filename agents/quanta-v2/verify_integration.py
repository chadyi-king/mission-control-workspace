#!/usr/bin/env python3
"""
QUANTA-V2 INTEGRATION TEST
Shows exactly how Telegram → Quanta → OANDA flow works
"""

import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*70)
print("QUANTA-V2 INTEGRATION FLOW VERIFICATION")
print("="*70)
print()

# Step 1: Telegram Monitor
print("STEP 1: TELEGRAM MONITOR (24/7 on Render)")
print("-"*70)
print("• Uses session file: quanta_session.session")
print("• Monitors: '🚀 CallistoFx Premium Channel 🚀'")
print("• Keep-alive: Every 5 minutes")
print("• Auto-reconnect: Yes (if disconnected)")
print()
print("When signal arrives:")
print('  Signal: "XAUUSD BUY 2680-2685, SL: 2675, TP1: 2690"')
print("  ↓")
print("  Parsed: symbol=XAUUSD, direction=BUY, entry=2680-2685, SL=2675")
print()

# Step 2: Signal Processing
print("STEP 2: SIGNAL PROCESSING")
print("-"*70)
print("• Parse symbol, direction, entry range, SL, TP levels")
print("• Validate all required fields present")
print("• Extract learning keywords from commentary")
print()

# Step 3: Position Sizing
print("STEP 3: POSITION SIZING (CRITICAL)")
print("-"*70)
print("• Query OANDA: 'What's the loss for 1 unit?'")
print("• Calculate: Units = $20 / loss_per_unit")
print("• Example: If 1 unit = $10.86 loss at SL")
print("           Then for $20 risk: 20 / 10.86 = 1.84 → 2 units")
print("• Verify: 2 units × $10.86 = $21.72 (close to $20)")
print()

# Step 4: Trade Execution
print("STEP 4: TRADE EXECUTION")
print("-"*70)
print("• 3-tier entry:")
print("  - Order 1: 33% of units at high of entry range")
print("  - Order 2: 33% of units at mid of entry range") 
print("  - Order 3: 34% of units at low of entry range")
print()
print("• SL management:")
print("  - Initial SL at 2675")
print("  - At +20 pips: Move SL to entry (break even)")
print("  - At +50 pips: Lock +20 pips profit")
print("  - At +100 pips: Activate runner with trailing SL")
print()
print("• TP management:")
print("  - TP1 (+20 pips): Close 10%")
print("  - TP2 (+40 pips): Close 10%")
print("  - TP3 (+60 pips): Close 10%")
print("  - TP4 (+80 pips): Close 10%")
print("  - TP5 (+100 pips): Close 10%, activate runner")
print()

# Step 5: Runner
print("STEP 5: RUNNER (After +100 pips)")
print("-"*70)
print("• Trailing SL: 100 pips behind current price")
print("• Every +50 pips: Close 10% of remaining position")
print("• Let winners run until SL hit")
print()

# Step 6: Reporting
print("STEP 6: REPORTING")
print("-"*70)
print("• Send trade details to Helios via Redis")
print("• Log all actions to quanta.log")
print("• Update trade status in real-time")
print()

print("="*70)
print("VERIFICATION CHECKLIST")
print("="*70)
print()
print("Before going live, verify:")
print()
print("[ ] OANDA connection works (balance shows correctly)")
print("[ ] Position size calculation is correct (~2 units for XAUUSD)")
print("[ ] Risk verification shows ~$20")
print("[ ] Telegram session file is valid")
print("[ ] CallistoFX channel is found and monitored")
print("[ ] Test trade executes correctly (paper trading)")
print("[ ] TP/SL modification works")
print("[ ] Runner activates at +100 pips")
print("[ ] Logs show 'Heartbeat OK' every 5 minutes")
print("[ ] Auto-reconnect works if disconnected")
print()

print("="*70)
print("MONITORING & SAFETY")
print("="*70)
print()
print("How I monitor Quanta 24/7:")
print()
print("1. Logs: Check quanta.log for errors")
print("2. Heartbeat: Verify 'Heartbeat OK' every 5 min")
print("3. Trades: Confirm each trade matches signal")
print("4. Redis: Receive reports from Quanta")
print("5. Alerts: Notify if anything goes wrong")
print()
print("Safety features:")
print("• Max position size cap (100k units)")
print("• Risk verification before every trade")
print("• Abort if risk > $30 (50% over target)")
print("• Account balance check (max 2% risk)")
print("• All trades logged with full details")
print()

print("="*70)
print("FLOW SUMMARY")
print("="*70)
print()
print("1. Telegram signal → Quanta receives it")
print("2. Quanta parses → Calculates position size")
print("3. Quanta verifies risk with OANDA")
print("4. Quanta executes 3-tier entry")
print("5. Quanta manages TP/SL automatically")
print("6. Quanta reports to Helios")
print("7. I monitor and alert if issues")
print()
print("="*70)
print()

# Test the actual calculation
print("TESTING ACTUAL CALCULATION:")
print()

try:
    from oanda_client import OandaClient
    
    client = OandaClient()
    balance = client.get_account_balance()
    
    print(f"✅ OANDA Connected")
    print(f"   Balance: {balance} SGD")
    print()
    
    # Test position size
    symbol = 'XAUUSD'
    entry = 2682.50
    stop_loss = 2675.00
    risk = 20.0
    
    print(f"Test: {symbol} at {entry}, SL {stop_loss}, Risk ${risk}")
    
    units = client.calculate_position_size(symbol, entry, stop_loss, risk)
    verified = client.verify_risk_before_trade(symbol, units, entry, stop_loss)
    
    print(f"   Calculated: {units} units")
    print(f"   Verified risk: ${verified:.2f}")
    
    if 15 <= verified <= 25:
        print(f"   ✅ Risk is within acceptable range ($15-25)")
    else:
        print(f"   ⚠️  Risk is outside target range")
    
except Exception as e:
    print(f"❌ Test failed: {e}")

print()
print("="*70)
print("Ready for Telegram authentication?")
print("="*70)
