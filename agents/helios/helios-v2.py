#!/usr/bin/env python3
"""
Helios v2.0 - Mission Control Engineer
Full tool access, Ollama integration, WebSocket messaging
"""

import sys
import os
import glob
import shutil
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/infrastructure')

from agent_client import AgentClient
import json
import logging
from datetime import datetime, timezone
import asyncio

try:
    import requests as _requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

HELIOS_API_URL = os.environ.get('HELIOS_API_URL', 'https://helios-api-xfvi.onrender.com').rstrip('/')

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
        """Run full audit cycle — includes Jobs 8, 9, 10"""
        logger.info(f"\n[{datetime.now().isoformat()}] Running audit...")

        findings = []

        # 1. Check data.json
        data_check = self.check_data_json()
        findings.extend(data_check.get('issues', []))

        # 2. Check all agents
        agent_checks = self.check_agents()
        findings.extend(agent_checks)

        # JOB 8: Scan agent outboxes for completed tasks
        completed = self.scan_agent_outboxes()
        if completed:
            logger.info(f"[Job8] {len(completed)} task(s) completed: {completed}")

        # 3. Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'auditor': 'helios',
            'findings': findings,
            'completed_tasks': completed,
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

        # JOB 9: POST dashboard snapshot to Helios API (broadcasts via WebSocket)
        agent_statuses = self._build_agent_status_snapshot()
        self.post_dashboard_snapshot(agent_statuses, findings)

        # JOB 10: Write DATA/data.json with live agent statuses
        self.write_dashboard_data(agent_statuses)

        # 5. Broadcast to other agents
        if findings:
            await self.client.broadcast('audit_complete', {
                'findings_count': len(findings),
                'urgent': [f for f in findings if f.get('severity') in ['critical', 'warning']][:3]
            })

    # ------------------------------------------------------------------ #
    # JOB 8 — Outbox Watcher
    # ------------------------------------------------------------------ #
    def scan_agent_outboxes(self):
        """Scan each agent outbox for new task-completion files. Mark done in DATA/data.json."""
        completed = []
        agents_dir = os.path.join(self.base_dir, 'agents')

        for outbox_path in glob.glob(os.path.join(agents_dir, '*', 'outbox', '*.json')):
            # Skip already-processed files
            if '/processed/' in outbox_path:
                continue
            try:
                with open(outbox_path) as f:
                    payload = json.load(f)

                task_id = payload.get('task_id') or payload.get('id')
                status = payload.get('status', '')

                if task_id and status in ('done', 'completed', 'complete'):
                    # Update DATA/data.json
                    self._mark_task_done_in_data(task_id)
                    completed.append(task_id)

                    # Move to processed/
                    processed_dir = os.path.join(os.path.dirname(outbox_path), 'processed')
                    os.makedirs(processed_dir, exist_ok=True)
                    shutil.move(outbox_path, os.path.join(processed_dir, os.path.basename(outbox_path)))
                    logger.info(f"[Job8] Marked done: {task_id}")

            except Exception as e:
                logger.warning(f"[Job8] Error processing {outbox_path}: {e}")

        return completed

    def _mark_task_done_in_data(self, task_id):
        """Mark a task as done in DATA/data.json"""
        data_path = os.path.join(self.base_dir, 'DATA', 'data.json')
        try:
            with open(data_path) as f:
                data = json.load(f)
            if task_id in data.get('tasks', {}):
                data['tasks'][task_id]['status'] = 'done'
                data['tasks'][task_id]['completedAt'] = datetime.now(timezone.utc).isoformat()
                # Move from workflow active/pending to done
                for stage in ('active', 'pending', 'review'):
                    if task_id in data.get('workflow', {}).get(stage, []):
                        data['workflow'][stage].remove(task_id)
                if task_id not in data.get('workflow', {}).get('done', []):
                    data['workflow'].setdefault('done', []).append(task_id)
                data['lastUpdated'] = datetime.now(timezone.utc).isoformat()
                with open(data_path, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"[Job8] Cannot update task {task_id}: {e}")

    # ------------------------------------------------------------------ #
    # JOB 9 — Dashboard Snapshot POST → WebSocket broadcast
    # ------------------------------------------------------------------ #
    def post_dashboard_snapshot(self, agent_statuses, findings):
        """POST a dashboard_snapshot event to Helios API. API broadcasts via /ws/dashboard."""
        if not REQUESTS_OK:
            logger.warning("[Job9] requests not available — skipping API push")
            return

        alert_count = len([f for f in findings if f.get('severity') in ('critical', 'warning')])
        payload = {
            'agent': 'helios',
            'ts': datetime.now(timezone.utc).isoformat(),
            'event_type': 'dashboard_snapshot',
            'payload': {
                'agents': agent_statuses,
                'alert_count': alert_count,
                'findings_summary': f"{len(findings)} findings, {alert_count} alerts"
            },
            'status': 'success',
            'idempotency_key': f"snapshot-{int(datetime.now().timestamp())}",
            'model_tier': 'cheap',
            'model_id': 'helios-v2-local',
            'reasoning_summary': '',
            'confidence': 1.0
        }
        try:
            resp = _requests.post(f"{HELIOS_API_URL}/api/events", json=payload, timeout=8)
            if resp.status_code == 200:
                logger.info(f"[Job9] Dashboard snapshot pushed to API")
            else:
                logger.warning(f"[Job9] API returned {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            logger.warning(f"[Job9] API push failed: {e}")

    # ------------------------------------------------------------------ #
    # JOB 10 — Write DATA/data.json with live agent statuses
    # ------------------------------------------------------------------ #
    def write_dashboard_data(self, agent_statuses):
        """Merge live agent statuses into DATA/data.json. Preserves task data."""
        data_path = os.path.join(self.base_dir, 'DATA', 'data.json')
        try:
            with open(data_path) as f:
                data = json.load(f)

            # Update system section
            now_sgt = datetime.now(timezone.utc).isoformat()
            data['lastUpdated'] = now_sgt
            data['updatedBy'] = 'helios-v2'

            # Update stats with real counts
            active_count = sum(1 for a in agent_statuses if a.get('status') == 'active')
            data['stats']['totalAgents'] = len(agent_statuses)
            data['stats']['activeAgents'] = active_count  # key dashboard JS expects

            # Update agent statuses block
            for agent in agent_statuses:
                name = agent.get('name', '').upper()
                if name in data.get('agents', {}):
                    data['agents'][name]['status'] = agent.get('status', 'unknown')
                    data['agents'][name]['last_seen'] = agent.get('last_seen')

            # Recalculate task counts from workflow arrays
            wf = data.get('workflow', {})
            data['stats']['pending'] = len(wf.get('pending', []))
            data['stats']['active'] = len(wf.get('active', []))
            data['stats']['review'] = len(wf.get('review', []))
            data['stats']['done'] = len(wf.get('done', []))

            # Count overdue
            today = datetime.now().date()
            overdue = [t for t in data.get('tasks', {}).values()
                       if t.get('deadline') and t.get('status') != 'done'
                       and datetime.strptime(t['deadline'], '%Y-%m-%d').date() < today]
            data['stats']['overdue'] = len(overdue)
            data['stats']['urgent'] = len([t for t in data.get('tasks', {}).values()
                                           if t.get('priority') == 'critical'
                                           and t.get('status') not in ('done', 'review')])

            # Also write root-level data.json (what the dashboard currently fetches)
            root_data_path = os.path.join(self.base_dir, 'data.json')
            root_data = {
                'schema': 'mission.control.dashboard.v1',
                'lastUpdated': now_sgt,
                'stats': {
                    'activeAgents': active_count,
                    'spawnedToday': active_count,
                    'tasksDone': data['stats'].get('done', 0),
                    'timeActive': '—',
                    'focusProject': 'A6',
                    'eventsToday': data['stats'].get('active', 0) + data['stats'].get('pending', 0)
                },
                'workflow': wf,
                'agents': data.get('agents', {}),
                'health': {
                    'last_audit': now_sgt,
                    'alerts': [],
                    'warnings': [f"{a['name']} blocked" for a in agent_statuses if a.get('status') == 'blocked']
                },
                'activity': []
            }

            # Atomic write with temp file
            tmp = data_path + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            shutil.move(tmp, data_path)

            tmp2 = root_data_path + '.tmp'
            with open(tmp2, 'w') as f:
                json.dump(root_data, f, indent=2)
            shutil.move(tmp2, root_data_path)

            logger.info(f"[Job10] DATA/data.json updated ({active_count} active agents)")

        except Exception as e:
            logger.error(f"[Job10] Failed to write dashboard data: {e}")

    def _build_agent_status_snapshot(self):
        """Build a list of agent status dicts from check_agents results"""
        agents = []
        names = ['chad-yi', 'helios', 'escritor', 'quanta', 'mensamusa', 'autour', 'forger']
        for name in names:
            result = self.client.exec(f'systemctl --user is-active {name} 2>/dev/null || echo "inactive"')
            svc = result.get('stdout', 'inactive').strip()
            proc = self.client.exec(f'ps aux | grep -E "{name}.*\.py" | grep -v grep | wc -l')
            proc_count = int(proc.get('stdout', '0').strip() or 0)
            status = 'active' if (svc == 'active' or proc_count > 0) else 'idle'
            agents.append({
                'name': name,
                'status': status,
                'last_seen': datetime.now(timezone.utc).isoformat()
            })
        return agents
    
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
