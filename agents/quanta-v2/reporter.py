import json
import redis
import logging
from datetime import datetime
from config import REDIS_URL, CHANNEL_OUT

logger = logging.getLogger(__name__)

class Reporter:
    """Report trades and status to Helios"""
    
    def __init__(self):
        self.redis_url = REDIS_URL
        self.channel = CHANNEL_OUT
        
        if self.redis_url:
            try:
                self.r = redis.from_url(self.redis_url)
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self.r = None
        else:
            self.r = None
    
    def _send(self, message):
        """Send message to Redis"""
        if not self.r:
            logger.warning("Redis not available, logging locally")
            logger.info(f"Would send: {message}")
            return False
        
        try:
            message['timestamp'] = datetime.now().isoformat()
            self.r.lpush(self.channel, json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            return False
    
    def report_trade_opened(self, signal, tiers, total_units):
        """Report new trade opened"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'trade_opened',
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'total_units': total_units,
            'tiers': tiers,
            'stop_loss': signal['stop_loss'],
            'take_profits': signal.get('take_profits', [])
        }
        self._send(report)
        logger.info(f"Reported trade opened: {signal['symbol']}")
    
    def report_tp_hit(self, trade_id, symbol, tp_level, pips, closed_units, remaining_units):
        """Report take profit hit"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'tp_hit',
            'trade_id': trade_id,
            'symbol': symbol,
            'tp_level': tp_level,
            'pips': pips,
            'closed_units': closed_units,
            'remaining_units': remaining_units
        }
        self._send(report)
        logger.info(f"Reported TP{tp_level} hit: +{pips} pips")
    
    def report_runner_activated(self, trade_id, symbol, remaining_units):
        """Report runner strategy activated"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'runner_activated',
            'trade_id': trade_id,
            'symbol': symbol,
            'remaining_units': remaining_units
        }
        self._send(report)
        logger.info(f"Runner activated for {symbol}")
    
    def report_sl_moved(self, trade_id, symbol, old_sl, new_sl, reason):
        """Report stop loss moved"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'sl_moved',
            'trade_id': trade_id,
            'symbol': symbol,
            'old_sl': old_sl,
            'new_sl': new_sl,
            'reason': reason
        }
        self._send(report)
        logger.info(f"SL moved: {old_sl} -> {new_sl} ({reason})")
    
    def report_trade_closed(self, trade_id, symbol, exit_price, pnl, pnl_pips, reason):
        """Report trade closed"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'trade_closed',
            'trade_id': trade_id,
            'symbol': symbol,
            'exit_price': exit_price,
            'pnl': pnl,
            'pnl_pips': pnl_pips,
            'reason': reason
        }
        self._send(report)
        logger.info(f"Trade closed: {symbol} P&L: ${pnl:.2f} ({pnl_pips} pips)")
    
    def report_error(self, error_message, details=None):
        """Report error"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'error',
            'error': error_message,
            'details': details or {}
        }
        self._send(report)
        logger.error(f"Error reported: {error_message}")
    
    def report_status(self, status, message=""):
        """Report agent status"""
        report = {
            'from': 'quanta-v2',
            'to': 'helios',
            'type': 'status',
            'status': status,
            'message': message
        }
        self._send(report)
