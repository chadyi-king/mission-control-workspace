#!/usr/bin/env python3
"""
Helios v2.0 - Mission Control Engineer
Full tool access, Ollama integration, WebSocket messaging
"""

import sys
import os
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/infrastructure')

from agent_client import AgentClient
import json
import logging
from datetime import datetime
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeliosAgent:
    def __init__(self):
        self.client = AgentClient('helios')
        self.base_dir = '/home/chad-yi/.openclaw/workspace'
        self.outbox_dir = os.path.join(self.base_dir, 'agents', 'helios', 'outbox')
        
    async def run(self):
        """Main agent loop"""
        logger.info("=" * 50)
        logger.info("HELIOS v2.0 - Mission Control Engineer Starting")
        logger.info("=" * 50)
        
        # Connect to infrastructure
        await self.client.connect()
        logger.info("Connected to hub")
        
        # Run audit immediately
        await self.run_audit()
        
        # Then loop
        while True:
            await asyncio.sleep(900)  # 15 minutes
            await self.run_audit()
    
    async def run_audit(self):
        """Run full audit cycle"""
        logger.info(f"\n[{datetime.now().isoformat()}] Running audit...")
        
        findings = []
        
        # 1. Check data.json
        data_check = self.check_data_json()
        findings.extend(data_check.get('issues', []))
        
        # 2. Check all agents
        agent_checks = self.check_agents()
        findings.extend(agent_checks)
        
        # 3. Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'auditor': 'helios',
            'findings': findings,
            'summary': {
                'total': len(findings),
                'critical': len([f for f in findings if f.get('severity') == 'critical']),
                'warning': len([f for f in findings if f.get('severity') == 'warning'])
            }
        }
        
        # 4. Write report
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        result = self.client.file_write(
            f'agents/helios/outbox/audit-{timestamp}.json',
            json.dumps(report, indent=2)
        )
        
        if result.get('success'):
            logger.info(f"✅ Audit complete: {len(findings)} findings")
        else:
            logger.error(f"Failed to write audit: {result}")
        
        # 5. Broadcast to other agents
        if findings:
            await self.client.broadcast('audit_complete', {
                'findings_count': len(findings),
                'urgent': [f for f in findings if f.get('severity') in ['critical', 'warning']][:3]
            })
    
    def check_data_json(self):
        """Check dashboard data integrity"""
        issues = []
        
        try:
            result = self.client.file_read('DATA/data.json')
            if 'error' in result:
                return {'issues': [{'severity': 'critical', 'issue': 'Cannot read data.json'}]}
            
            data = json.loads(result['content'])
            
            # Check lastUpdated
            if 'lastUpdated' in data:
                last = datetime.fromisoformat(data['lastUpdated'].replace('Z', '+00:00'))
                age_hours = (datetime.now() - last.replace(tzinfo=None)).total_seconds() / 3600
                if age_hours > 4:
                    issues.append({'severity': 'warning', 'issue': f'data.json stale: {age_hours:.1f}h'})
            
            # Check for overdue tasks
            if 'tasks' in data:
                today = datetime.now().date()
                for task_id, task in data['tasks'].items():
                    if task.get('deadline') and task.get('status') != 'done':
                        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d').date()
                        if deadline < today:
                            issues.append({'severity': 'warning', 'issue': f'Overdue: {task_id}'})
                        elif deadline == today:
                            issues.append({'severity': 'warning', 'issue': f'Due today: {task_id}'})
            
        except Exception as e:
            issues.append({'severity': 'critical', 'issue': f'Audit error: {e}'})
        
        return {'issues': issues}
    
    def check_agents(self):
        """Check agent health"""
        issues = []
        agents = ['forger', 'escritor', 'quanta', 'mensamusa', 'autour']
        
        for agent in agents:
            # Check if service is running
            result = self.client.exec(f'systemctl --user is-active {agent} 2>/dev/null || echo "inactive"')
            status = result.get('stdout', '').strip()
            
            if status != 'active':
                issues.append({'severity': 'warning', 'agent': agent, 'issue': f'Service {status}'})
            
            # Check inbox for stale messages
            inbox_result = self.client.exec(f'ls ~/.openclaw/workspace/agents/{agent}/inbox/ 2>/dev/null | wc -l')
            inbox_count = int(inbox_result.get('stdout', '0').strip() or 0)
            
            if inbox_count > 0:
                issues.append({'severity': 'info', 'agent': agent, 'issue': f'{inbox_count} unread messages'})
        
        return issues

if __name__ == '__main__':
    agent = HeliosAgent()
    asyncio.run(agent.run())
