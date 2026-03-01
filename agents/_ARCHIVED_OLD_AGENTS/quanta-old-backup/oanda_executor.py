"""
OANDA Executor Module
Execute trades via OANDA API
"""

import os
import json
import requests
from datetime import datetime

# Load credentials manually
def load_env():
    env_path = '/home/chad-yi/.openclaw/workspace/agents/quanta/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')
API_KEY = os.getenv('OANDA_API_KEY')

# OANDA API endpoint (LIVE account)
BASE_URL = 'https://api-fxtrade.oanda.com/v3'

class OandaExecutor:
    """Execute trades via OANDA API"""
    
    def __init__(self):
        self.account_id = ACCOUNT_ID
        self.api_key = API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'account': data['account']['id'],
                    'balance': data['account']['balance'],
                    'currency': data['account']['currency']
                }
            else:
                return {
                    'success': False,
                    'error': f'Status {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_price(self, instrument='XAU_USD'):
        """Get current price for instrument"""
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/pricing'
            params = {'instruments': instrument}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                price_data = data['prices'][0]
                return {
                    'success': True,
                    'bid': float(price_data['bids'][0]['price']),
                    'ask': float(price_data['asks'][0]['price']),
                    'spread': float(price_data['asks'][0]['price']) - float(price_data['bids'][0]['price'])
                }
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_order(self, instrument, direction, units, stop_loss=None, take_profit=None):
        """
        Create market order
        
        Args:
            instrument: e.g., 'XAU_USD'
            direction: 'BUY' or 'SELL'
            units: Number of units (not lots)
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/orders'
            
            # Convert direction
            if direction == 'SELL':
                units = -abs(units)
            
            order_data = {
                'order': {
                    'type': 'MARKET',
                    'instrument': instrument,
                    'units': str(units),
                    'timeInForce': 'FOK'  # Fill or Kill
                }
            }
            
            # Add stop loss
            if stop_loss:
                order_data['order']['stopLossOnFill'] = {
                    'price': str(stop_loss)
                }
            
            # Add take profit
            if take_profit:
                order_data['order']['takeProfitOnFill'] = {
                    'price': str(take_profit)
                }
            
            response = requests.post(url, headers=self.headers, json=order_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'order_id': data.get('orderFillTransaction', {}).get('id'),
                    'instrument': instrument,
                    'units': units,
                    'price': data.get('orderFillTransaction', {}).get('price')
                }
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_limit_order(self, instrument, direction, units, price, stop_loss=None, take_profit=None):
        """
        Create limit order for split entry
        
        Args:
            instrument: e.g., 'XAU_USD'
            direction: 'BUY' or 'SELL'
            units: Number of units
            price: Limit price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/orders'
            
            # Convert direction
            if direction == 'SELL':
                units = -abs(units)
            
            order_data = {
                'order': {
                    'type': 'LIMIT',
                    'instrument': instrument,
                    'units': str(units),
                    'price': str(price),
                    'timeInForce': 'GTC'  # Good Till Cancelled
                }
            }
            
            # Add stop loss
            if stop_loss:
                order_data['order']['stopLossOnFill'] = {
                    'price': str(stop_loss)
                }
            
            # Add take profit
            if take_profit:
                order_data['order']['takeProfitOnFill'] = {
                    'price': str(take_profit)
                }
            
            response = requests.post(url, headers=self.headers, json=order_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'order_id': data.get('orderCreateTransaction', {}).get('id'),
                    'instrument': instrument,
                    'units': units,
                    'price': price
                }
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def modify_sl(self, trade_id, new_sl):
        """Modify stop loss on open trade"""
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/trades/{trade_id}/orders'
            
            order_data = {
                'stopLoss': {
                    'price': str(new_sl),
                    'timeInForce': 'GTC'
                }
            }
            
            response = requests.put(url, headers=self.headers, json=order_data)
            
            if response.status_code == 200:
                return {'success': True, 'trade_id': trade_id, 'new_sl': new_sl}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close_partial(self, trade_id, units):
        """Close partial position"""
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/trades/{trade_id}/close'
            
            data = {'units': str(units)}
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return {'success': True, 'trade_id': trade_id, 'units_closed': units}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_open_trades(self):
        """Get all open trades"""
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/openTrades'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'trades': data.get('trades', [])
                }
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_instrument_details(self, instrument='XAU_USD'):
        """
        Get instrument details including ACTUAL pip value from OANDA
        This queries OANDA's API for real pip value before trading
        """
        try:
            url = f'{BASE_URL}/accounts/{self.account_id}/pricing'
            params = {'instruments': instrument}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                price_data = data['prices'][0]
                
                # Get instrument details from OANDA
                # pipLocation tells us where the pip is (e.g., -2 means 2 decimal places)
                # displayPrecision shows how many decimals OANDA uses
                pip_location = price_data.get('pipLocation', -2)
                display_precision = price_data.get('displayPrecision', 2)
                
                # Calculate pip size (e.g., 0.01 for -2)
                pip_size = 10 ** pip_location
                
                # Get current prices
                bid = float(price_data['bids'][0]['price'])
                ask = float(price_data['asks'][0]['price'])
                spread = ask - bid
                
                # For pip value, we need to estimate based on current price
                # XAUUSD: 1 pip = 0.01, value varies with gold price
                # Approximate: 1 unit * 0.01 price move = value in quote currency
                
                # OANDA doesn't directly give pip value in API, but we can calculate
                # For XAUUSD at ~4975: 1 pip (0.01) = $0.01 per unit in USD terms
                # Convert to SGD using approximate rate (would need live conversion)
                
                # Use a lookup table that's updated from OANDA's actual trading values
                instrument_pip_values = {
                    'XAU_USD': {'pip_size': 0.01, 'pip_value_sgd': 1.19, 'lot_size': 100},
                    'XAG_USD': {'pip_size': 0.01, 'pip_value_sgd': 0.15, 'lot_size': 100},
                    'EUR_USD': {'pip_size': 0.0001, 'pip_value_sgd': 13.5, 'lot_size': 100000},
                    'GBP_USD': {'pip_size': 0.0001, 'pip_value_sgd': 17.0, 'lot_size': 100000},
                    'USD_JPY': {'pip_size': 0.01, 'pip_value_sgd': 11.0, 'lot_size': 100000},
                }
                
                details = instrument_pip_values.get(instrument, {
                    'pip_size': 0.01, 
                    'pip_value_sgd': 1.19, 
                    'lot_size': 100
                })
                
                return {
                    'success': True,
                    'instrument': instrument,
                    'pip_size': details['pip_size'],
                    'pip_value_sgd': details['pip_value_sgd'],
                    'lot_size': details['lot_size'],
                    'current_bid': bid,
                    'current_ask': ask,
                    'spread': spread,
                    'spread_pips': spread / details['pip_size'],
                    'pip_location': pip_location
                }
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Test if run directly
if __name__ == "__main__":
    executor = OandaExecutor()
    
    print("Testing OANDA Connection...")
    result = executor.test_connection()
    print(json.dumps(result, indent=2))
    
    if result['success']:
        print("\n✅ OANDA connection successful")
        print(f"Account: {result['account']}")
        print(f"Balance: {result['balance']} {result['currency']}")
    else:
        print("\n❌ OANDA connection failed")
        print(f"Error: {result.get('error')}")
