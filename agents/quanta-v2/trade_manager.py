import logging
import json
import os
from config import (
    RISK_AMOUNT, RISK_PERCENT_AFTER_20, TRADE_COUNT_FILE,
    TIER_SPLITS, TP_LEVELS, TP_CLOSE_PERCENT,
    RUNNER_ACTIVATION_PIPS, RUNNER_TRAIL_DISTANCE,
    RUNNER_CLOSE_PERCENT, RUNNER_STEP_PIPS,
    SL_BE_ACTIVATION, SL_LOCK_ACTIVATION, SL_LOCK_PROFIT
)

logger = logging.getLogger(__name__)

class TradeManager:
    """Manage trade execution and lifecycle"""
    
    def __init__(self, oanda_client, reporter):
        self.oanda = oanda_client
        self.reporter = reporter
        self.active_trades = {}  # trade_id -> trade info
        self.trade_count = self._load_trade_count()
    
    def _load_trade_count(self):
        """Load trade count from file"""
        if os.path.exists(TRADE_COUNT_FILE):
            try:
                with open(TRADE_COUNT_FILE, 'r') as f:
                    return json.load(f).get('count', 0)
            except:
                return 0
        return 0
    
    def _save_trade_count(self):
        """Save trade count to file"""
        try:
            with open(TRADE_COUNT_FILE, 'w') as f:
                json.dump({'count': self.trade_count}, f)
        except Exception as e:
            logger.error(f"Error saving trade count: {e}")
    
    def get_risk_amount(self, account_balance=10000):
        """Get current risk amount"""
        if self.trade_count < 20:
            return RISK_AMOUNT  # $20 fixed
        else:
            return account_balance * RISK_PERCENT_AFTER_20  # 1-2%
    
    def execute_3tier_entry(self, signal):
        """Execute 3-tier split entry"""
        symbol = signal['symbol']
        direction = signal['direction']
        entry_high = signal['entry_high']
        entry_mid = signal['entry_mid']
        entry_low = signal['entry_low']
        stop_loss = signal['stop_loss']
        
        # Calculate total position size
        risk_amount = self.get_risk_amount()
        
        # Use mid price for calculation
        mid_price = (entry_high + entry_low) / 2
        total_units = self.oanda.calculate_position_size(symbol, mid_price, stop_loss, risk_amount)
        
        if total_units == 0:
            logger.error("Failed to calculate position size")
            return None
        
        # Verify risk with OANDA - CRITICAL SAFETY CHECK
        verified_risk = self.oanda.verify_risk(symbol, total_units, mid_price, stop_loss)
        
        if verified_risk < 0:
            logger.error("RISK VERIFICATION FAILED - ABORTING TRADE")
            return None
        
        if verified_risk > risk_amount * 1.5:
            logger.error(f"RISK TOO HIGH: ${verified_risk:.2f} (max allowed: ${risk_amount * 1.5:.2f})")
            return None
        
        logger.info(f"Verified risk: ${verified_risk:.2f}")
        
        # Split into 3 tiers
        tiers = []
        entries = [entry_high, entry_mid, entry_low]
        
        for i, (split, entry_price) in enumerate(zip(TIER_SPLITS, entries)):
            tier_units = int(total_units * split)
            
            # Create order
            order = self.oanda.create_order(
                symbol=symbol,
                direction=direction,
                units=tier_units,
                entry=entry_price,
                stop_loss=stop_loss
            )
            
            if order:
                tiers.append({
                    'tier': i + 1,
                    'units': tier_units,
                    'entry': entry_price,
                    'order_id': order['id']
                })
                logger.info(f"Tier {i+1}: {tier_units} units @ {entry_price}")
            else:
                logger.error(f"Failed to create tier {i+1}")
        
        if tiers:
            self.trade_count += 1
            self._save_trade_count()
            
            # Report to Helios
            self.reporter.report_trade_opened(signal, tiers, total_units)
            
            # Store active trade
            trade_id = f"{symbol}_{direction}_{self.trade_count}"
            self.active_trades[trade_id] = {
                'symbol': symbol,
                'direction': direction,
                'tiers': tiers,
                'total_units': total_units,
                'remaining_units': total_units,
                'entry_price': mid_price,
                'stop_loss': stop_loss,
                'highest_pnl': 0,
                'runner_active': False,
                'tp_count': 0
            }
            
            return trade_id
        
        return None
    
    def monitor_and_manage(self, trade_id):
        """Monitor open trade and manage TPs/SLs"""
        if trade_id not in self.active_trades:
            return
        
        trade = self.active_trades[trade_id]
        symbol = trade['symbol']
        
        # Get open trades from OANDA
        open_trades = self.oanda.get_open_trades()
        
        for oanda_trade in open_trades:
            if oanda_trade['instrument'].replace('_', '') == symbol:
                current_price = float(oanda_trade['price'])
                unrealized_pnl = float(oanda_trade.get('unrealizedPL', 0))
                
                # Calculate pips
                pips = self._calculate_pips(symbol, trade['entry_price'], current_price, trade['direction'])
                
                # Track highest PnL
                if pips > trade['highest_pnl']:
                    trade['highest_pnl'] = pips
                
                # Check TP levels
                self._check_take_profits(trade_id, trade, pips, oanda_trade['id'])
                
                # Check SL management
                self._manage_stop_loss(trade_id, trade, pips, oanda_trade['id'])
                
                # Check runner
                if trade['runner_active']:
                    self._manage_runner(trade_id, trade, pips, oanda_trade['id'])
    
    def _calculate_pips(self, symbol, entry, current, direction):
        """Calculate pips gained/lost"""
        diff = current - entry
        
        if direction == 'SELL':
            diff = -diff
        
        if symbol in ['XAUUSD', 'XAGUSD']:
            return diff * 10  # 0.1 = 1 pip
        else:
            return diff * 10000  # 0.0001 = 1 pip
    
    def _check_take_profits(self, trade_id, trade, pips, oanda_trade_id):
        """Check and execute take profits"""
        if trade['runner_active']:
            return  # Runner mode handles this
        
        for tp_pips in TP_LEVELS:
            if pips >= tp_pips and trade['tp_count'] < TP_LEVELS.index(tp_pips) + 1:
                # Close 10% at this TP
                close_units = int(trade['total_units'] * TP_CLOSE_PERCENT)
                
                if close_units > 0 and trade['remaining_units'] >= close_units:
                    self.oanda.close_trade(oanda_trade_id, close_units)
                    trade['remaining_units'] -= close_units
                    trade['tp_count'] += 1
                    
                    self.reporter.report_tp_hit(
                        trade_id, trade['symbol'], TP_LEVELS.index(tp_pips) + 1,
                        tp_pips, close_units, trade['remaining_units']
                    )
                    
                    logger.info(f"TP hit: +{tp_pips} pips, closed {close_units} units")
                    
                    # Check if runner should activate
                    if tp_pips == RUNNER_ACTIVATION_PIPS:
                        trade['runner_active'] = True
                        self.reporter.report_runner_activated(trade_id, trade['symbol'], trade['remaining_units'])
                        logger.info("Runner activated!")
    
    def _manage_stop_loss(self, trade_id, trade, pips, oanda_trade_id):
        """Manage stop loss movements"""
        current_sl = trade['stop_loss']
        entry = trade['entry_price']
        
        # Move to BE at +20 pips
        if pips >= SL_BE_ACTIVATION and current_sl != entry:
            new_sl = entry
            if self.oanda.modify_trade(oanda_trade_id, stop_loss=new_sl):
                trade['stop_loss'] = new_sl
                self.reporter.report_sl_moved(trade_id, trade['symbol'], current_sl, new_sl, 'breakeven')
                logger.info(f"SL moved to BE: {new_sl}")
        
        # Lock +20 pips at +50 pips
        elif pips >= SL_LOCK_ACTIVATION and trade['stop_loss'] == entry:
            if trade['direction'] == 'BUY':
                new_sl = entry + (SL_LOCK_PROFIT / 10000)
            else:
                new_sl = entry - (SL_LOCK_PROFIT / 10000)
            
            if self.oanda.modify_trade(oanda_trade_id, stop_loss=new_sl):
                trade['stop_loss'] = new_sl
                self.reporter.report_sl_moved(trade_id, trade['symbol'], entry, new_sl, 'lock_profit')
                logger.info(f"SL locked at +{SL_LOCK_PROFIT} pips: {new_sl}")
    
    def _manage_runner(self, trade_id, trade, pips, oanda_trade_id):
        """Manage runner strategy"""
        if not trade['runner_active']:
            return
        
        # Calculate runner level (how many +50 pips beyond +100)
        runner_pips = pips - RUNNER_ACTIVATION_PIPS
        runner_level = int(runner_pips / RUNNER_STEP_PIPS)
        
        # Trail SL (100 pips behind current)
        if trade['direction'] == 'BUY':
            trail_sl = trade['entry_price'] + ((pips - RUNNER_TRAIL_DISTANCE) / 10000)
        else:
            trail_sl = trade['entry_price'] - ((pips - RUNNER_TRAIL_DISTANCE) / 10000)
        
        if trail_sl > trade['stop_loss']:
            if self.oanda.modify_trade(oanda_trade_id, stop_loss=trail_sl):
                old_sl = trade['stop_loss']
                trade['stop_loss'] = trail_sl
                self.reporter.report_sl_moved(trade_id, trade['symbol'], old_sl, trail_sl, 'trailing')
        
        # Close 10% of remaining every +50 pips
        if runner_level > 0 and runner_level > getattr(trade, 'last_runner_level', 0):
            close_units = int(trade['remaining_units'] * RUNNER_CLOSE_PERCENT)
            
            if close_units > 0:
                self.oanda.close_trade(oanda_trade_id, close_units)
                trade['remaining_units'] -= close_units
                trade['last_runner_level'] = runner_level
                
                logger.info(f"Runner: closed {close_units} units at +{pips} pips, remaining: {trade['remaining_units']}")
    
    def close_all(self, trade_id, reason='manual'):
        """Close entire trade"""
        if trade_id not in self.active_trades:
            return
        
        trade = self.active_trades[trade_id]
        
        # Close all tiers
        for tier in trade['tiers']:
            self.oanda.close_trade(tier['order_id'])
        
        self.reporter.report_trade_closed(
            trade_id, trade['symbol'], 0, 0, trade['highest_pnl'], reason
        )
        
        del self.active_trades[trade_id]
        logger.info(f"Trade {trade_id} closed: {reason}")
