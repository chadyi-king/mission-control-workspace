#!/usr/bin/env python3
"""
Quanta OANDA Trading Bot
Connects to OANDA API, executes trades from CALLISTOFX signals
"""

import json
import requests
from datetime import datetime
from oanda_config import (
    OANDA_API_KEY, 
    OANDA_ACCOUNT_ID, 
    OANDA_ENVIRONMENT,
    RISK_PERCENT_PER_TRADE,
    MAX_OPEN_POSITIONS,
    AUTO_EXECUTE_SIGNALS
)

# OANDA API Endpoints
if OANDA_ENVIRONMENT == "live":
    BASE_URL = "https://api-fxtrade.oanda.com/v3"
else:
    BASE_URL = "https://api-fxpractice.oanda.com/v3"

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

class OANDAClient:
    def __init__(self):
        self.account_id = OANDA_ACCOUNT_ID
        self.base_url = BASE_URL
        
    def get_account_summary(self):
        """Get account balance and margin info"""
        url = f"{self.base_url}/accounts/{self.account_id}/summary"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            account = data['account']
            return {
                'balance': float(account['balance']),
                'nav': float(account['NAV']),
                'margin_used': float(account['marginUsed']),
                'margin_available': float(account['marginAvailable']),
                'open_trade_count': int(account['openTradeCount']),
                'currency': account['currency']
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def get_open_positions(self):
        """Get all open positions"""
        url = f"{self.base_url}/accounts/{self.account_id}/openPositions"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            return response.json()['positions']
        return []
    
    def execute_trade(self, pair, action, units, stop_loss=None, take_profit=None):
        """
        Execute a market order trade
        
        Args:
            pair: Currency pair (e.g., "EUR_USD", "XAU_USD")
            action: "BUY" or "SELL"
            units: Number of units to trade
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
        """
        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        
        # Format pair for OANDA (replace / with _)
        instrument = pair.replace("/", "_")
        
        # Determine units sign based on action
        if action.upper() == "SELL":
            units = -abs(units)
        else:
            units = abs(units)
        
        order_data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "timeInForce": "FOK"
            }
        }
        
        # Add stop loss if provided
        if stop_loss:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(stop_loss)
            }
        
        # Add take profit if provided
        if take_profit:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(take_profit)
            }
        
        response = requests.post(url, headers=HEADERS, json=order_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Trade executed: {action} {abs(units)} units of {instrument}")
            return result
        else:
            print(f"❌ Trade failed: {response.status_code} - {response.text}")
            return None
    
    def process_callistofx_signal(self, signal):
        """
        Process a trading signal from CALLISTOFX
        
        Expected signal format:
        {
            'action': 'BUY' or 'SELL',
            'pair': 'EURUSD' or 'XAUUSD',
            'entry': 1.0850,
            'stop_loss': 1.0820,
            'take_profit': 1.0900
        }
        """
        print(f"\n📊 Processing CALLISTOFX signal:")
        print(f"   Action: {signal['action']}")
        print(f"   Pair: {signal['pair']}")
        print(f"   Entry: {signal.get('entry', 'MARKET')}")
        print(f"   SL: {signal.get('stop_loss', 'N/A')}")
        print(f"   TP: {signal.get('take_profit', 'N/A')}")
        
        # Check if auto-execute is enabled
        if not AUTO_EXECUTE_SIGNALS:
            print("   ⚠️ AUTO_EXECUTE_SIGNALS is False - trade NOT executed")
            print("   Set AUTO_EXECUTE_SIGNALS = True in config to enable automatic trading")
            return None
        
        # Get account balance for position sizing
        account = self.get_account_summary()
        if not account:
            print("   ❌ Could not get account info")
            return None
        
        # Check max open positions
        if account['open_trade_count'] >= MAX_OPEN_POSITIONS:
            print(f"   ⚠️ Max open positions ({MAX_OPEN_POSITIONS}) reached")
            return None
        
        # Calculate position size based on risk
        balance = account['balance']
        risk_amount = balance * (RISK_PERCENT_PER_TRADE / 100)
        
        # For now, use fixed units (can improve with proper position sizing)
        units = 1000  # Micro lot - adjust based on account size
        
        # Execute the trade
        pair = signal['pair']
        action = signal['action']
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')
        
        result = self.execute_trade(pair, action, units, stop_loss, take_profit)
        
        # Log the trade
        if result:
            trade_log = {
                'timestamp': datetime.now().isoformat(),
                'signal': signal,
                'result': result,
                'account_balance': balance
            }
            
            with open('/agents/quanta/inbox/trades_executed.jsonl', 'a') as f:
                f.write(json.dumps(trade_log) + '\n')
        
        return result

def test_connection():
    """Test OANDA API connection"""
    print("🔌 Testing OANDA connection...")
    print(f"   Environment: {OANDA_ENVIRONMENT.upper()}")
    print(f"   Account ID: {OANDA_ACCOUNT_ID}")
    
    client = OANDAClient()
    account = client.get_account_summary()
    
    if account:
        print(f"\n✅ Connection successful!")
        print(f"   Balance: {account['currency']} {account['balance']:,.2f}")
        print(f"   NAV: {account['currency']} {account['nav']:,.2f}")
        print(f"   Margin Available: {account['currency']} {account['margin_available']:,.2f}")
        print(f"   Open Trades: {account['open_trade_count']}")
        return True
    else:
        print("\n❌ Connection failed")
        return False

def main():
    """Main entry point"""
    import sys
    
    print("=" * 50)
    print("Quanta OANDA Trading Bot")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    print(f"Environment: {OANDA_ENVIRONMENT.upper()}")
    print(f"Auto-Execute: {AUTO_EXECUTE_SIGNALS}")
    print("=" * 50)
    
    # Test connection
    if not test_connection():
        sys.exit(1)
    
    print("\n📡 Bot is ready to receive CALLISTOFX signals")
    print("   Waiting for signals...")
    
    # TODO: Integrate with Telegram monitor to auto-process signals
    # For now, manual signal processing

if __name__ == '__main__':
    main()
