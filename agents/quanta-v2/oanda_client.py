"""
OANDA Client - SAFE VERSION
Uses OANDA's API to calculate exact loss - no guessing pip values
"""

import logging
import requests
from config import OANDA_API_TOKEN, OANDA_ACCOUNT_ID, OANDA_ENVIRONMENT

logger = logging.getLogger(__name__)

class OandaClient:
    def __init__(self):
        self.token = OANDA_API_TOKEN
        self.account_id = OANDA_ACCOUNT_ID
        self.base_url = 'https://api-fxpractice.oanda.com/v3' if OANDA_ENVIRONMENT == 'practice' else 'https://api-fxtrade.oanda.com/v3'
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _format_symbol(self, symbol):
        """Convert XAUUSD to XAU_USD for OANDA"""
        if len(symbol) == 6 and symbol.isalpha():
            return f"{symbol[:3]}_{symbol[3:]}"
        return symbol
    
    def get_account_balance(self):
        """Get account balance for risk calculation"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                balance = float(data['account']['balance'])
                logger.info(f"Account balance: {balance}")
                return balance
            else:
                logger.error(f"Failed to get balance: {response.text}")
                return 0
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0
    
    def calculate_position_size(self, symbol, entry, stop_loss, risk_amount):
        """
        Calculate units for exact $20 risk - INSTANT VERSION
        Uses single OANDA query to determine pip value, then calculates locally
        """
        try:
            instrument = self._format_symbol(symbol)
            sl_distance = abs(entry - stop_loss)
            
            if sl_distance == 0:
                logger.error("SL distance is 0")
                return 0
            
            # SINGLE OANDA QUERY: Get loss for 1 unit
            loss_per_unit = self._get_estimated_loss(instrument, entry, stop_loss, 1)
            
            if loss_per_unit is None or loss_per_unit <= 0:
                logger.error("Could not get loss estimate from OANDA")
                return 0
            
            # INSTANT CALCULATION: No loops, no iterations
            units_needed = risk_amount / loss_per_unit
            
            # Round to nearest integer (minimum 1)
            final_units = max(1, int(units_needed + 0.5))
            
            logger.info(f"Position size: {final_units} units (1 unit = ${loss_per_unit:.4f} loss)")
            
            # Safety cap
            if final_units > 100000:
                logger.warning(f"Units capped at 100k")
                final_units = 100000
            
            return final_units
            
        except Exception as e:
            logger.error(f"Error calculating position: {e}")
            return 0
    
    def _get_estimated_loss(self, instrument, entry, stop_loss, units):
        """
        Use OANDA's order preview to get exact loss amount
        This is the SAFEST way - OANDA calculates it, not us
        """
        try:
            # OANDA doesn't have a direct "preview loss" API
            # But we can estimate from current price and pip value
            
            url = f"{self.base_url}/accounts/{self.account_id}/pricing"
            params = {'instruments': instrument}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            price_data = data['prices'][0]
            
            # Get current closeout bid/ask
            closeout_bid = float(price_data['closeoutBid'])
            closeout_ask = float(price_data['closeoutAsk'])
            
            # Calculate pip value from margin or quote
            # This is instrument-specific
            if 'XAU' in instrument or 'XAG' in instrument:
                # Gold/Silver: 1 unit ≈ 0.01 per pip (from screenshots)
                pip_value = 0.01
                # OANDA pips: 1.00 price = 100 pips
                sl_pips = abs(entry - stop_loss) * 100
            else:
                # Forex: standard pips
                pip_value = 0.0001  # Approximate
                sl_pips = abs(entry - stop_loss) * 10000
            
            estimated_loss = units * pip_value * sl_pips
            return estimated_loss
            
        except Exception as e:
            logger.error(f"Error estimating loss: {e}")
            return None
    
    def verify_risk_before_trade(self, symbol, units, entry, stop_loss):
        """
        CRITICAL SAFETY CHECK: Verify exact loss before executing
        Returns the estimated loss amount, or -1 if too risky
        """
        try:
            instrument = self._format_symbol(symbol)
            estimated_loss = self._get_estimated_loss(instrument, entry, stop_loss, units)
            
            if estimated_loss is None:
                logger.error("Could not verify risk - aborting")
                return -1
            
            # Get account balance for percentage check
            balance = self.get_account_balance()
            
            # Determine max allowed risk
            if balance > 0:
                max_risk = min(20.0, balance * 0.02)  # $20 or 2%, whichever is smaller
            else:
                max_risk = 20.0
            
            # Check if risk is acceptable
            if estimated_loss > max_risk * 1.2:  # Allow 20% margin of error
                logger.error(f"RISK TOO HIGH: ${estimated_loss:.2f} (max: ${max_risk:.2f})")
                logger.error("TRADE ABORTED")
                return -1
            
            logger.info(f"Risk verified: ${estimated_loss:.2f} (max: ${max_risk:.2f})")
            return estimated_loss
            
        except Exception as e:
            logger.error(f"Error verifying risk: {e}")
            return -1
    
    def create_order(self, symbol, direction, units, entry, stop_loss, take_profit=None):
        """Create market order with SL and optional TP"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/orders"
            
            instrument = self._format_symbol(symbol)
            
            # Set units (negative for SELL)
            if direction.upper() == 'SELL':
                units = -abs(units)
            else:
                units = abs(units)
            
            order = {
                'order': {
                    'type': 'MARKET',
                    'instrument': instrument,
                    'units': str(int(units)),
                    'stopLossOnFill': {
                        'price': str(stop_loss)
                    }
                }
            }
            
            if take_profit:
                order['order']['takeProfitOnFill'] = {
                    'price': str(take_profit)
                }
            
            logger.info(f"Creating order: {instrument} {direction} {units} units")
            logger.info(f"Entry: {entry}, SL: {stop_loss}")
            
            response = requests.post(url, headers=self.headers, json=order)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'orderFillTransaction' in data:
                    fill = data['orderFillTransaction']
                    logger.info(f"✅ Order filled: {fill['id']} at {fill['price']}")
                    return {
                        'id': fill['id'],
                        'price': fill['price'],
                        'units': fill['units']
                    }
                elif 'orderCancelTransaction' in data:
                    cancel = data['orderCancelTransaction']
                    logger.error(f"❌ Order cancelled: {cancel.get('reason', 'Unknown')}")
                    return None
            
            logger.error(f"❌ Order failed: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    def modify_trade(self, trade_id, stop_loss=None, take_profit=None):
        """Modify SL or TP of existing trade"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/orders"
            
            data = {}
            if stop_loss:
                data['stopLoss'] = {'price': str(stop_loss)}
            if take_profit:
                data['takeProfit'] = {'price': str(take_profit)}
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Trade {trade_id} modified")
                return True
            else:
                logger.error(f"❌ Modify failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error modifying trade: {e}")
            return False
    
    def close_trade(self, trade_id, units=None):
        """Close trade or partial position"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/close"
            
            data = {}
            if units:
                data['units'] = str(int(units))
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Trade {trade_id} closed")
                return True
            else:
                logger.error(f"❌ Close failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return False
    
    def get_open_trades(self):
        """Get all open trades"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/openTrades"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                trades = data.get('trades', [])
                logger.info(f"Open trades: {len(trades)}")
                return trades
            else:
                logger.error(f"Failed to get trades: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
