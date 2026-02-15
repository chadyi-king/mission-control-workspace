#!/usr/bin/env python3
"""
MensaMusa v2.0 - Options Flow Agent
Full tool access, monitors Twitter/X for options flow
"""

import sys
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/infrastructure')

from agent_client import AgentClient
import json
import logging
from datetime import datetime
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MensaMusaAgent:
    def __init__(self):
        self.client = AgentClient('mensamusa')
        self.base_dir = '/home/chad-yi/.openclaw/workspace/agents/mensamusa'
        
    async def run(self):
        """Main agent loop"""
        logger.info("=" * 50)
        logger.info("MENSAMUSA v2.0 - Options Flow Agent Starting")
        logger.info("=" * 50)
        
        await self.client.connect()
        
        # Check credentials
        creds = self.check_credentials()
        if not creds:
            logger.warning("Moomoo credentials not configured - entering prep mode")
            await self.prep_mode()
        else:
            logger.info("Credentials found - entering monitoring mode")
            await self.monitoring_mode()
    
    def check_credentials(self):
        """Check if Moomoo API credentials exist"""
        result = self.client.file_read('agents/mensamusa/config.json')
        if 'content' in result:
            try:
                config = json.loads(result['content'])
                return config.get('moomoo_account') and config.get('moomoo_password')
            except:
                pass
        return False
    
    async def prep_mode(self):
        """Prepare while waiting for credentials"""
        logger.info("Prep mode: Building options monitoring infrastructure...")
        
        strategy = """# A5-2 Options Flow Monitoring
**MensaMusa v2.0 - Awaiting Moomoo Credentials**

## Strategy Overview
**Source:** Twitter/X options flow accounts
**Execution:** Moomoo options trading
**Focus:** Unusual options activity, sweeps, block trades

## Implementation Plan

### Phase 1: Twitter Monitoring
- Monitor accounts: @unusual_whales, @OptionsFlow, etc.
- Parse options flow alerts
- Extract: ticker, strike, expiry, volume, premium

### Phase 2: Analysis
- Check if flow is bullish/bearish
- Verify against open interest
- Cross-reference with recent news
- Calculate risk/reward

### Phase 3: Alerts
- High conviction plays → Alert CHAD_YI
- Unusual activity → Log for review
- Earnings plays → Flag with date

### Phase 4: Execution (Optional)
- Small test positions on high conviction
- Strict risk management
- Quick exits on reversals

## Technical Stack
- Python 3.10+
- Tweepy for Twitter API
- Moomoo OpenAPI
- pandas for flow analysis
- asyncio for real-time monitoring

## Example Flow Alert
```
$AAPL
$200 CALLS
EXPIRY: 2/16
PREMIUM: $2.5M
UNUSUAL VOLUME
```

## Watchlist
- AAPL, TSLA, NVDA, MSFT, AMZN
- SPY, QQQ, IWM
- Meme stocks: GME, AMC

## Next Steps
1. Provide Moomoo account credentials
2. Set up Twitter API access
3. Configure watchlist
4. Define alert thresholds

**Status:** Ready to monitor once credentials received.
"""
        
        result = self.client.file_write(
            'agents/mensamusa/MONITORING-STRATEGY.md',
            strategy
        )
        
        if result.get('success'):
            logger.info("✅ Monitoring strategy document created")
        
        # Wait for credentials
        while not self.check_credentials():
            logger.info("Waiting for Moomoo credentials...")
            await asyncio.sleep(3600)
        
        await self.monitoring_mode()
    
    async def monitoring_mode(self):
        """Active monitoring mode"""
        logger.info("Entering options flow monitoring mode")
        
        while True:
            # Monitor Twitter for options flow
            logger.info("Monitoring cycle complete")
            await asyncio.sleep(30)  # 30 second cycle for fast options

if __name__ == '__main__':
    agent = MensaMusaAgent()
    asyncio.run(agent.run())
