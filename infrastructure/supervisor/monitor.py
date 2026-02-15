#!/usr/bin/env python3
"""
Agent Supervisor
Monitors all agents and restarts crashed services
"""

import subprocess
import time
import json
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AGENTS = [
    {'name': 'helios', 'enabled': True},
    {'name': 'forger', 'enabled': True},
    {'name': 'escritor', 'enabled': False},  # Not yet autonomous
    {'name': 'quanta', 'enabled': False},
    {'name': 'mensamusa', 'enabled': False},
    {'name': 'autour', 'enabled': False}
]

INFRASTRUCTURE = [
    {'name': 'agent-hub', 'port': 9000, 'cmd': 'python3 infrastructure/hub/websocket-server.py'},
    {'name': 'tool-bridge', 'port': 9001, 'cmd': 'python3 infrastructure/tool-bridge/server.py'}
]

class Supervisor:
    def __init__(self):
        self.base_dir = os.path.expanduser('~/.openclaw/workspace')
        
    def check_service(self, service_name):
        """Check if systemd service is running"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'is-active', service_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking {service_name}: {e}")
            return False
    
    def restart_service(self, service_name):
        """Restart a systemd service"""
        try:
            logger.warning(f"Restarting {service_name}...")
            subprocess.run(
                ['systemctl', '--user', 'restart', service_name],
                capture_output=True,
                check=True
            )
            logger.info(f"✅ {service_name} restarted")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restart {service_name}: {e}")
            return False
    
    def check_infrastructure(self):
        """Check infrastructure services"""
        for svc in INFRASTRUCTURE:
            # Check if process is running on port
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{svc["port"]}'],
                    capture_output=True,
                    text=True
                )
                running = result.returncode == 0
                
                if not running:
                    logger.warning(f"{svc['name']} not running on port {svc['port']}")
                    # Could auto-restart here
                else:
                    logger.info(f"✅ {svc['name']} healthy on port {svc['port']}")
                    
            except Exception as e:
                logger.error(f"Error checking {svc['name']}: {e}")
    
    def check_agents(self):
        """Check all agent services"""
        for agent in AGENTS:
            if not agent['enabled']:
                continue
                
            running = self.check_service(agent['name'])
            
            if running:
                logger.info(f"✅ {agent['name']} running")
            else:
                logger.warning(f"⚠️  {agent['name']} not running")
                self.restart_service(agent['name'])
    
    def run_cycle(self):
        """One monitoring cycle"""
        logger.info("=" * 50)
        logger.info(f"Supervisor Check - {datetime.now().isoformat()}")
        logger.info("=" * 50)
        
        self.check_infrastructure()
        self.check_agents()
        
        logger.info("Cycle complete. Sleeping 30s...")
        logger.info("")
    
    def run(self):
        """Main supervisor loop"""
        logger.info("=" * 50)
        logger.info("AGENT SUPERVISOR STARTING")
        logger.info("Monitoring all agents and infrastructure")
        logger.info("=" * 50)
        
        while True:
            try:
                self.run_cycle()
                time.sleep(30)
            except Exception as e:
                logger.error(f"Supervisor error: {e}")
                time.sleep(5)

if __name__ == '__main__':
    supervisor = Supervisor()
    supervisor.run()
