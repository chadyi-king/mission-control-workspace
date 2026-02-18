import json
import logging
import requests
from datetime import datetime
from config import REDIS_URL

logger = logging.getLogger(__name__)

class Reporter:
    """Report Quanta status and trades to Helios via HTTP"""
    
    def __init__(self):
        self.redis_url = REDIS_URL
        # HTTP endpoint for reporting (REST API)
        self.http_endpoint = "https://national-gar-36005.upstash.io/lpush/quanta-helios"
        self.http_token = "AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU"
    
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
            
            # Send via HTTP
            response = requests.post(
                self.http_endpoint,
                headers={'Authorization': f'Bearer {self.http_token}'},
                data=json.dumps(report),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Reported status: {status}")
            else:
                logger.warning(f"HTTP report failed: {response.status_code}")
                
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
            
            response = requests.post(
                self.http_endpoint,
                headers={'Authorization': f'Bearer {self.http_token}'},
                data=json.dumps(report),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Reported trade: {trade_data.get('symbol', 'unknown')}")
            else:
                logger.warning(f"HTTP report failed: {response.status_code}")
                
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
                'message': message_text[:200]  # First 200 chars
            }
            
            response = requests.post(
                self.http_endpoint,
                headers={'Authorization': f'Bearer {self.http_token}'},
                data=json.dumps(report),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Reported message: {msg_type}")
            else:
                logger.warning(f"HTTP report failed: {response.status_code}")
                
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
            
            response = requests.post(
                self.http_endpoint,
                headers={'Authorization': f'Bearer {self.http_token}'},
                data=json.dumps(report),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Reported error: {error_type}")
            else:
                logger.warning(f"HTTP report failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to report error: {e}")
