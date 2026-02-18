import json
import logging
import requests
from datetime import datetime
from config import REDIS_URL, CHANNEL_OUT

logger = logging.getLogger(__name__)

class Reporter:
    """Report Quanta status and trades to Helios via Redis REST API"""
    
    def __init__(self):
        # Parse Redis URL for REST API
        # URL format: redis://default:PASSWORD@HOST:PORT
        self.redis_url = REDIS_URL
        self.channel_out = CHANNEL_OUT
        
        # Extract credentials from Redis URL
        try:
            # redis://default:PASSWORD@HOST:PORT
            parts = self.redis_url.replace('redis://', '').split('@')
            if len(parts) == 2:
                auth = parts[0]  # default:PASSWORD
                host_port = parts[1]  # HOST:PORT
                self.token = auth.split(':')[1] if ':' in auth else auth
                self.host = host_port.split(':')[0]
                self.port = host_port.split(':')[1] if ':' in host_port else '6379'
                self.rest_url = f"https://{self.host}/lpush/{self.channel_out}"
                self.connected = True
            else:
                self.connected = False
                logger.error("Could not parse Redis URL")
        except Exception as e:
            self.connected = False
            logger.error(f"Redis setup failed: {e}")
    
    def _send_to_redis(self, data):
        """Send data to Redis via REST API"""
        try:
            if not self.connected:
                return False
            
            response = requests.post(
                self.rest_url,
                headers={'Authorization': f'Bearer {self.token}'},
                data=json.dumps(data),
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Redis send failed: {e}")
            return False
    
    def report_status(self, status, message):
        """Report current status"""
        try:
            report = {
                'from': 'quanta-v2',
                'to': 'helios',
                'type': 'status',
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'message': message
            }
            
            if self._send_to_redis(report):
                logger.info(f"✅ Reported status to Redis: {status}")
            else:
                logger.warning("Redis report failed, logging locally")
                logger.info(f"Status: {status} - {message}")
                
        except Exception as e:
            logger.error(f"Failed to report status: {e}")
    
    def report_trade(self, trade_data):
        """Report trade execution"""
        try:
            report = {
                'from': 'quanta-v2',
                'to': 'helios',
                'type': 'trade',
                'timestamp': datetime.now().isoformat(),
                'trade': trade_data
            }
            
            if self._send_to_redis(report):
                logger.info(f"✅ Reported trade to Redis: {trade_data.get('symbol', 'unknown')}")
            else:
                logger.warning("Redis report failed, logging locally")
                
        except Exception as e:
            logger.error(f"Failed to report trade: {e}")
    
    def report_message(self, message_text, msg_type='unknown'):
        """Report received message"""
        try:
            report = {
                'from': 'quanta-v2',
                'to': 'helios',
                'type': 'message',
                'timestamp': datetime.now().isoformat(),
                'msg_type': msg_type,
                'message': message_text[:200]
            }
            
            if self._send_to_redis(report):
                logger.info(f"✅ Reported message to Redis: {msg_type}")
            else:
                logger.warning("Redis report failed, logging locally")
                
        except Exception as e:
            logger.error(f"Failed to report message: {e}")
    
    def report_error(self, error_type, details):
        """Report errors"""
        try:
            report = {
                'from': 'quanta-v2',
                'to': 'helios',
                'type': 'error',
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type,
                'details': details
            }
            
            if self._send_to_redis(report):
                logger.info(f"✅ Reported error to Redis: {error_type}")
            else:
                logger.warning("Redis report failed, logging locally")
                
        except Exception as e:
            logger.error(f"Failed to report error: {e}")
