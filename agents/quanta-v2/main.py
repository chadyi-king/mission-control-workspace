#!/usr/bin/env python3
"""
Quanta-v2 Trading Bot - Main Entry Point
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
import pytz

# Set timezone to Singapore
os.environ['TZ'] = 'Asia/Singapore'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quanta.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import components
from config import REDIS_URL, CHANNEL_IN
from oanda_client import OandaClient
from signal_parser import SignalParser
from trade_manager import TradeManager
from learning_engine import LearningEngine
from reporter import Reporter

class QuantaV2:
    """Main Quanta trading bot"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info("Quanta-v2 Starting...")
        logger.info("=" * 60)
        
        # Initialize components
        self.oanda = OandaClient()
        self.parser = SignalParser()
        self.learning = LearningEngine()
        self.reporter = Reporter()
        self.trade_manager = TradeManager(self.oanda, self.reporter)
        
        # Signal queue (until Telegram is added)
        self.signal_queue = []
        
        self.reporter.report_status('active', 'Quanta-v2 initialized')
        logger.info("All components initialized")
    
    def process_signal(self, signal_text):
        """Process a trading signal"""
        logger.info(f"Processing signal: {signal_text[:100]}...")
        
        # Parse signal
        signal = self.parser.parse(signal_text)
        
        if not signal:
            logger.warning("Failed to parse signal")
            return False
        
        if not self.parser.validate(signal):
            logger.warning("Signal validation failed")
            return False
        
        # Execute trade
        trade_id = self.trade_manager.execute_3tier_entry(signal)
        
        if trade_id:
            logger.info(f"Trade executed: {trade_id}")
            return True
        else:
            logger.error("Trade execution failed")
            return False
    
    def process_message(self, text, msg_type='unknown'):
        """Process any message from Telegram"""
        logger.info(f"Processing [{msg_type}]: {text[:100]}...")
        
        if msg_type == 'signal':
            # Process trading signal
            self.process_signal(text)
        
        elif msg_type == 'result':
            # Process trade results for learning
            logger.info("Trade result recorded for learning")
            # Could update win/loss statistics
        
        elif msg_type == 'commentary':
            # Process educational commentary
            lesson = self.process_commentary(text)
            logger.info(f"Learned: {lesson.get('strategies', [])}")
        
        else:
            logger.debug(f"Unknown message type: {msg_type}")
    
    def monitor_trades(self):
        """Monitor and manage open trades"""
        for trade_id in list(self.trade_manager.active_trades.keys()):
            self.trade_manager.monitor_and_manage(trade_id)
    
    def run_test_signal(self):
        """Run with test signal (for testing without Telegram)"""
        test_signal = "XAUUSD BUY 2680-2685, SL: 2675, TP1: 2690, TP2: 2700"
        logger.info(f"Test signal: {test_signal}")
        self.process_signal(test_signal)
    
    def run(self):
        """Main loop"""
        logger.info("Starting main loop...")
        
        try:
            while True:
                # Check for new signals (from queue until Telegram added)
                if self.signal_queue:
                    signal = self.signal_queue.pop(0)
                    self.process_signal(signal)
                
                # Monitor open trades
                self.monitor_trades()
                
                # Sleep before next iteration
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.reporter.report_status('stopped', 'Manual shutdown')
        except Exception as e:
            logger.error(f"Critical error: {e}")
            self.reporter.report_error('Critical error', {'error': str(e)})
            raise

def main():
    """Entry point"""
    quanta = QuantaV2()
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        logger.info("Running in test mode...")
        quanta.run_test_signal()
        # Keep monitoring
        try:
            while True:
                quanta.monitor_trades()
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Test complete")
    else:
        quanta.run()

if __name__ == '__main__':
    main()
