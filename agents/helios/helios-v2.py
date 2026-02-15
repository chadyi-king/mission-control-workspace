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
        
    async def handle_message(self, msg_type, payload, sender):
        """Handle incoming messages from other agents"""
        logger.info(f"[{self.client.agent_id}] Received {msg_type} from {sender}")
        
        if msg_type == 'status_request':
            # Report current status
            await self.client.send_to(sender, 'status_report', {
                'agent': 'helios',
                'status': 'running',
                'last_audit': datetime.now().isoformat(),
                'active_tasks': ['auditing']
            })
            
        elif msg_type == 'audit_request':
            # Run immediate audit
            logger.info("Running on-demand audit...")
            await self.run_audit()
            await self.client.send_to(sender, 'audit_done', {
                'timestamp': datetime.now().isoformat()
            })
            
        elif msg_type == 'task_complete':
            # Another agent finished a task - log it
            logger.info(f"Task complete from {sender}: {payload}")
            # Update dashboard
            await self.update_dashboard_task(payload)
            
        elif msg_type == 'help_request':
            # Agent needs help
            logger.warning(f"Help requested by {sender}: {payload}")
            # Could escalate to CHAD_YI
            
        else:
            logger.info(f"Unhandled message type: {msg_type}")
        
    async def run(self):
        """Main agent loop with message handling"""
        logger.info("=" * 50)
        logger.info("HELIOS v2.0 - Mission Control Engineer Starting")
        logger.info("=" * 50)
        
        # Override client's handle_message to use ours
        self.client._handle_message = self._wrap_handle_message
        
        # Connect to infrastructure
        await self.client.connect()
        logger.info("Connected to hub")
        
        # Run audit immediately
        await self.run_audit()
        
        # Then loop - handle messages AND run audits
        while True:
            await asyncio.sleep(60)  # Check every minute
            # Audit runs every 15 minutes automatically
            if datetime.now().minute % 15 == 0:
                await self.run_audit()
    
    async def _wrap_handle_message(self, data):
        """Wrapper to route messages to handle_message"""
        await self.handle_message(
            data.get('type'),
            data.get('payload', {}),
            data.get('from', 'unknown')
        )
    
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
        """Check agent health - systemd services AND running processes"""
        issues = []
        agents = ['forger', 'escritor', 'quanta', 'mensamusa', 'autour']
        
        for agent in agents:
            # Check if service is running (systemd)
            result = self.client.exec(f'systemctl --user is-active {agent} 2>/dev/null || echo "inactive"')
            service_status = result.get('stdout', '').strip()
            
            # Also check if process is running directly (for non-systemd agents like Quanta)
            process_check = self.client.exec(f'ps aux | grep -E "{agent}.*\.py|monitor_{agent}" | grep -v grep | wc -l')
            process_count = int(process_check.get('stdout', '0').strip() or 0)
            
            is_running = (service_status == 'active') or (process_count > 0)
            
            if not is_running:
                issues.append({'severity': 'warning', 'agent': agent, 'issue': f'Not running (service: {service_status}, processes: {process_count})'})
            else:
                # Agent is running - update dashboard status
                logger.info(f"✅ {agent} is active")
            
            # Check inbox for stale messages
            inbox_result = self.client.exec(f'ls ~/.openclaw/workspace/agents/{agent}/inbox/ 2>/dev/null | wc -l')
            inbox_count = int(inbox_result.get('stdout', '0').strip() or 0)
            
            if inbox_count > 0:
                issues.append({'severity': 'info', 'agent': agent, 'issue': f'{inbox_count} unread messages'})
        
        return issues
    
    async def update_dashboard_task(self, payload):
        """Update dashboard when agent completes task"""
        try:
            task_id = payload.get('task_id')
            status = payload.get('status')
            
            if task_id and status == 'done':
                # Mark task as done in data.json
                result = self.client.file_read('DATA/data.json')
                if 'content' in result:
                    data = json.loads(result['content'])
                    if task_id in data.get('tasks', {}):
                        data['tasks'][task_id]['status'] = 'done'
                        data['tasks'][task_id]['completedAt'] = datetime.now().isoformat()
                        
                        # Write back
                        self.client.file_write('DATA/data.json', json.dumps(data, indent=2))
                        logger.info(f"✅ Updated dashboard: {task_id} marked done")
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")

if __name__ == '__main__':
    agent = HeliosAgent()
    asyncio.run(agent.run())
