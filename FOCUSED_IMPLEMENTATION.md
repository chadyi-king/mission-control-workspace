# FOCUSED IMPLEMENTATION: CHAD_YI → Helios → Dashboard → Cerebronn
## Fix the Core Flow First

**Priority Order:**
1. CHAD_YI → Helios (coordination)
2. Helios → Dashboard (sync)
3. Cerebronn (The Brain - fix/replace)

---

# PART 1: CHAD_YI → HELIOS FLOW

## Current Problem

**What's Broken:**
- CHAD_YI can't notify you of status changes
- Helios runs but you don't see updates
- No feedback loop

**What We Need:**
```
CHAD_YI monitors → Detects change → Notifies you → You respond → Action taken
```

## Implementation

### Step 1: Create Status Monitor

**File:** `agents/chad-yi/monitor.py`

```python
#!/usr/bin/env python3
"""
CHAD_YI Monitor - Check systems and report changes
"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import json
import time
from pathlib import Path
from datetime import datetime
from agent_base import AgentBase, Task, Result


class StatusMonitor(AgentBase):
    """
    Monitors system status and reports changes to human
    """
    
    def __init__(self):
        super().__init__('chad-yi', {
            'poll_interval': 300,  # Check every 5 minutes
            'use_database': True
        })
        
        self.last_status = {}
        self.alert_threshold = 2  # Alert after 2 consecutive issues
    
    def execute(self, task: Task) -> Result:
        if task.type == 'CHECK_STATUS':
            return self.check_all_systems()
        elif task.type == 'FORCE_CHECK':
            return self.check_all_systems(force=True)
        return Result(task.id, False, f"Unknown: {task.type}")
    
    def check_all_systems(self, force=False):
        """Check all systems and report changes"""
        alerts = []
        
        # 1. Check Helios
        helios_status = self.check_helios()
        if helios_status['changed'] or force:
            alerts.append(self.format_helios_alert(helios_status))
        
        # 2. Check Dashboard
        dashboard_status = self.check_dashboard()
        if dashboard_status['changed'] or force:
            alerts.append(self.format_dashboard_alert(dashboard_status))
        
        # 3. Check for urgent tasks
        urgent = self.check_urgent_tasks()
        if urgent:
            alerts.append(self.format_urgent_alert(urgent))
        
        # 4. Write alerts to outbox (for human to read)
        if alerts:
            self.write_alert_report(alerts)
            return Result('check', True, {'alerts': len(alerts)})
        
        return Result('check', True, {'alerts': 0})
    
    def check_helios(self):
        """Check Helios status"""
        state_file = self.workspace / 'agents' / 'helios' / 'state.json'
        
        if not state_file.exists():
            return {
                'changed': True,
                'status': 'missing',
                'message': 'Helios state file not found'
            }
        
        try:
            state = json.loads(state_file.read_text())
            current = {
                'status': state.get('status'),
                'last_heartbeat': state.get('last_heartbeat'),
                'errors_today': state.get('errors_today', 0)
            }
            
            # Check if changed
            changed = current != self.last_status.get('helios')
            self.last_status['helios'] = current
            
            # Check for problems
            if current['errors_today'] > 0:
                return {
                    'changed': True,
                    'status': 'error',
                    'message': f"Helios has {current['errors_today']} errors today",
                    'details': current
                }
            
            return {
                'changed': changed,
                'status': current['status'],
                'message': f"Helios: {current['status']}",
                'details': current
            }
            
        except Exception as e:
            return {
                'changed': True,
                'status': 'error',
                'message': f"Failed to read Helios state: {e}"
            }
    
    def check_dashboard(self):
        """Check dashboard data freshness"""
        data_file = self.workspace / 'mission-control-dashboard' / 'data.json'
        
        if not data_file.exists():
            return {
                'changed': True,
                'status': 'missing',
                'message': 'Dashboard data.json not found'
            }
        
        try:
            data = json.loads(data_file.read_text())
            last_updated = data.get('lastUpdated')
            
            if last_updated:
                last_time = datetime.fromisoformat(last_updated)
                age_minutes = (datetime.now() - last_time).total_seconds() / 60
                
                if age_minutes > 30:  # Older than 30 minutes
                    return {
                        'changed': True,
                        'status': 'stale',
                        'message': f"Dashboard data is {age_minutes:.0f} minutes old",
                        'last_updated': last_updated
                    }
                
                return {
                    'changed': False,
                    'status': 'fresh',
                    'message': f"Dashboard updated {age_minutes:.0f} minutes ago",
                    'stats': data.get('stats', {})
                }
            
        except Exception as e:
            return {
                'changed': True,
                'status': 'error',
                'message': f"Failed to read dashboard: {e}"
            }
    
    def check_urgent_tasks(self):
        """Check for urgent/overdue tasks"""
        data_file = self.workspace / 'mission-control-dashboard' / 'data.json'
        
        if not data_file.exists():
            return []
        
        try:
            data = json.loads(data_file.read_text())
            tasks = data.get('tasks', {})
            
            urgent = []
            for task_id, task in tasks.items():
                if task.get('status') == 'blocked':
                    urgent.append(task)
                # Could add deadline checking here
            
            return urgent
            
        except:
            return []
    
    def format_helios_alert(self, status):
        """Format Helios status for human"""
        if status['status'] == 'error':
            return f"🚨 HELIOS ERROR\n{status['message']}"
        return f"🟢 Helios: {status['message']}"
    
    def format_dashboard_alert(self, status):
        """Format dashboard status for human"""
        if status['status'] == 'stale':
            return f"⚠️ DASHBOARD STALE\n{status['message']}\nCheck Helios is running"")
        elif status['status'] == 'fresh' and 'stats' in status:
            s = status['stats']
            return f"📊 Dashboard Status\nTotal: {s.get('total', 0)} | Pending: {s.get('pending', 0)} | Active: {s.get('active', 0)} | Blocked: {s.get('blocked', 0)}"
        return f"Dashboard: {status['message']}"
    
    def format_urgent_alert(self, urgent_tasks):
        """Format urgent tasks for human"""
        lines = ["🔴 URGENT TASKS"]
        for task in urgent_tasks[:5]:  # Top 5
            lines.append(f"• {task.get('id', 'unknown')}: {task.get('title', 'No title')}")
        return "\n".join(lines)
    
    def write_alert_report(self, alerts):
        """Write alerts to outbox for human to read"""
        report = {
            'type': 'STATUS_REPORT',
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts,
            'summary': f"{len(alerts)} status updates"
        }
        
        report_file = self.outbox / f"STATUS_{datetime.now():%Y%m%d_%H%M%S}.md"
        
        content = f"""# Status Report - {datetime.now():%Y-%m-%d %H:%M}

{chr(10).join(alerts)}

---
Reply with questions or actions needed.
"""
        report_file.write_text(content)
        self.logger.info(f"Wrote status report: {report_file.name}")


if __name__ == '__main__':
    monitor = StatusMonitor()
    monitor.run()
```

### Step 2: Create Human-Readable Reports

**File:** `agents/chad-yi/report_generator.py`

```python
#!/usr/bin/env python3
"""
Generate human-readable reports from system data
"""

import json
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw/workspace'
    
    def generate_daily_report(self):
        """Generate daily status report"""
        data_file = self.workspace / 'mission-control-dashboard' / 'data.json'
        
        if not data_file.exists():
            return "❌ Dashboard data not available"
        
        data = json.loads(data_file.read_text())
        stats = data.get('stats', {})
        tasks = data.get('tasks', {})
        agents = data.get('agents', {})
        
        # Count urgent
        urgent = [t for t in tasks.values() if t.get('status') == 'blocked']
        
        report = f"""
📊 DAILY REPORT - {datetime.now():%A, %B %d, %Y}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tasks: {stats.get('total', 0)}
  • Pending: {stats.get('pending', 0)}
  • Active: {stats.get('active', 0)}
  • Blocked: {stats.get('blocked', 0)} {'🔴' if urgent else ''}
  • Done: {stats.get('done', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for name, status in agents.items():
            symbol = "🟢" if status.get('status') == 'active' else "🔴" if status.get('status') == 'error' else "⚪"
            report += f"{symbol} {name}: {status.get('status', 'unknown')}\n"
        
        if urgent:
            report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 URGENT ATTENTION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for task in urgent[:5]:
                report += f"• {task.get('id')}: {task.get('title', 'Untitled')}\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next: Review and prioritize
Reply with task IDs to focus on.
"""
        
        return report
    
    def generate_urgent_alert(self, task_id):
        """Generate urgent alert for specific task"""
        data_file = self.workspace / 'mission-control-dashboard' / 'data.json'
        
        if not data_file.exists():
            return None
        
        data = json.loads(data_file.read_text())
        task = data.get('tasks', {}).get(task_id)
        
        if not task:
            return None
        
        return f"""
🔴 URGENT: {task_id}

{task.get('title', 'Untitled')}
Status: {task.get('status', 'unknown')}

Action required. Reply with:
• "START" - Begin working on it
• "BLOCKED [reason]" - Mark as blocked
• "DELEGATE [agent]" - Assign to agent
"""


# Test
generator = ReportGenerator()
print(generator.generate_daily_report())
```

---

# PART 2: HELIOS → DASHBOARD (Fix Sync)

## Current Problem

Helios may be running but:
- Data.json not updating
- Git push failing silently
- Dashboard showing stale data

## Fix Implementation

### Step 1: Enhanced Helios with Verification

**File:** `agents/helios/helios_fixed.py`

```python
#!/usr/bin/env python3
"""
Helios Fixed - With verification and error reporting
"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import json
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime
from agent_base import AgentBase, Task, Result


class HeliosFixed(AgentBase):
    """
    Enhanced Helios with verification
    """
    
    def __init__(self):
        super().__init__('helios', {
            'poll_interval': 900,  # 15 minutes
            'use_database': False
        })
        
        self.dashboard_dir = self.workspace / 'mission-control-dashboard'
        self.active_file = self.workspace / 'ACTIVE.md'
        self.last_sync_success = True
    
    def execute(self, task: Task) -> Result:
        if task.type in ['SCHEDULED_SYNC', 'FORCE_SYNC']:
            return self.sync_with_verification()
        return Result(task.id, False, error=f"Unknown: {task.type}")
    
    def sync_with_verification(self) -> Result:
        """
        Sync with full verification
        Returns detailed result for CHAD_YI to report
        """
        steps = []
        
        try:
            # Step 1: Read ACTIVE.md
            self.logger.info("Step 1: Reading ACTIVE.md")
            if not self.active_file.exists():
                error = "ACTIVE.md not found"
                self.logger.error(error)
                self.report_failure(error)
                return Result('sync', False, error=error)
            
            content = self.active_file.read_text()
            steps.append("✓ Read ACTIVE.md")
            
            # Step 2: Parse
            self.logger.info("Step 2: Parsing tasks")
            tasks = self.parse_active_md(content)
            steps.append(f"✓ Parsed {len(tasks)} tasks")
            
            # Step 3: Calculate stats
            self.logger.info("Step 3: Calculating stats")
            stats = self.calculate_stats(tasks)
            steps.append(f"✓ Stats: {stats}")
            
            # Step 4: Build data.json
            self.logger.info("Step 4: Building data.json")
            data = {
                'lastUpdated': datetime.now().isoformat(),
                'updatedBy': 'Helios',
                'version': '2.0',
                'stats': stats,
                'tasks': tasks,
                'agents': self.get_agent_status()
            }
            
            data_file = self.dashboard_dir / 'data.json'
            temp_file = data_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.rename(data_file)  # Atomic write
            steps.append("✓ Wrote data.json")
            
            # Step 5: Verify write
            self.logger.info("Step 5: Verifying write")
            if not data_file.exists():
                error = "data.json write failed"
                self.report_failure(error)
                return Result('sync', False, error=error)
            
            # Verify content
            try:
                verify_data = json.loads(data_file.read_text())
                if verify_data.get('lastUpdated') != data['lastUpdated']:
                    error = "data.json verification failed - timestamp mismatch"
                    self.report_failure(error)
                    return Result('sync', False, error=error)
            except Exception as e:
                error = f"data.json verification failed: {e}"
                self.report_failure(error)
                return Result('sync', False, error=error)
            
            steps.append("✓ Verified data.json")
            
            # Step 6: Git push
            self.logger.info("Step 6: Git push")
            git_result = self.git_push()
            if git_result['success']:
                steps.append(f"✓ Git push: {git_result['message']}")
            else:
                steps.append(f"⚠ Git push: {git_result['message']}")
                # Don't fail for git issues, just warn
            
            # Success!
            self.last_sync_success = True
            self.logger.info(f"Sync complete: {stats['total']} tasks")
            
            return Result(
                'sync',
                True,
                {
                    'tasks_synced': stats['total'],
                    'steps': steps,
                    'stats': stats
                }
            )
            
        except Exception as e:
            self.logger.exception("Sync failed")
            self.report_failure(str(e))
            self.last_sync_success = False
            return Result('sync', False, error=str(e))
    
    def report_failure(self, error):
        """Report failure to CHAD_YI outbox"""
        report_file = (self.workspace / 'agents' / 'chad-yi' / 'inbox' / 
                      f"HELIOS_ERROR_{datetime.now():%Y%m%d_%H%M%S}.md")
        
        content = f"""# 🚨 Helios Error Report

**Time:** {datetime.now():%Y-%m-%d %H:%M:%S}
**Error:** {error}

**Action Required:**
1. Check Helios logs: `journalctl --user -u helios -n 50`
2. Verify ACTIVE.md exists and is valid
3. Check disk space
4. Restart Helios if needed: `systemctl --user restart helios`

**Last Successful Sync:** {self.last_sync_success}
"""
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(content)
        self.logger.info(f"Error report written: {report_file}")
    
    def git_push(self):
        """Git push with detailed result"""
        try:
            # Check if git repo exists
            git_dir = self.dashboard_dir / '.git'
            if not git_dir.exists():
                return {'success': False, 'message': 'Not a git repository'}
            
            # Add
            add_result = subprocess.run(
                ['git', 'add', 'data.json'],
                cwd=self.dashboard_dir,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                return {'success': False, 'message': f'git add failed: {add_result.stderr}'}
            
            # Check if there are changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.dashboard_dir,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                return {'success': True, 'message': 'No changes to push'}
            
            # Commit
            commit_result = subprocess.run(
                ['git', 'commit', '-m', f'Helios: {datetime.now():%Y-%m-%d %H:%M:%S}'],
                cwd=self.dashboard_dir,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                return {'success': False, 'message': f'git commit failed: {commit_result.stderr}'}
            
            # Push
            push_result = subprocess.run(
                ['git', 'push'],
                cwd=self.dashboard_dir,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                return {'success': True, 'message': 'Pushed successfully'}
            else:
                return {'success': False, 'message': f'git push failed: {push_result.stderr}'}
                
        except Exception as e:
            return {'success': False, 'message': f'Git error: {e}'}
    
    # ... [rest of methods from original Helios]
    def parse_active_md(self, content: str) -> dict:
        tasks = {}
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                current_section = line[3:].strip().lower()
                continue
            
            if line.strip().startswith('- [') and current_section:
                match = re.match(r'- \[(.)\] ([A-C]\d+-\d+): (.+?)(?:\s*\((.+?)\))?$', line.strip())
                if match:
                    status_mark = match.group(1)
                    task_id = match.group(2)
                    title = match.group(3)
                    
                    if status_mark == 'x':
                        status = 'done'
                    elif current_section == 'active':
                        status = 'active'
                    elif current_section == 'blocked':
                        status = 'blocked'
                    else:
                        status = 'pending'
                    
                    tasks[task_id] = {
                        'id': task_id,
                        'title': title,
                        'status': status
                    }
        
        return tasks
    
    def calculate_stats(self, tasks: dict) -> dict:
        stats = {'total': len(tasks), 'pending': 0, 'active': 0, 'blocked': 0, 'done': 0}
        for task in tasks.values():
            status = task.get('status', 'pending')
            if status in stats:
                stats[status] += 1
        return stats
    
    def get_agent_status(self) -> dict:
        agents = {}
        agents_dir = self.workspace / 'agents'
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                state_file = agent_dir / 'state.json'
                if state_file.exists():
                    try:
                        state = json.loads(state_file.read_text())
                        agents[agent_dir.name] = {
                            'status': state.get('status', 'unknown'),
                            'lastHeartbeat': state.get('last_heartbeat')
                        }
                    except:
                        agents[agent_dir.name] = {'status': 'error'}
        return agents


if __name__ == '__main__':
    agent = HeliosFixed()
    agent.run()
```

---

# PART 3: CEREBRONN (The Brain)

## Current State

**Problem:**
- AI model not responding via OpenClaw API
- Connection issues
- Cannot generate content

## Solutions

### Option A: Fix Current Cerebronn

**Check:**
```bash
# Test API connection
python3 -c "
import openai
client = openai.OpenAI(
    api_key='your-key',
    base_url='https://api.openclaw.ai/v1'
)
response = client.chat.completions.create(
    model='claude-3.5-sonnet',
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print(response)
"
```

**If fails:** Need to fix API connection or switch models

### Option B: Replace with Local Brain

**Use Ollama + Local Model:**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull reasoning model
ollama pull llama3.1:70b

# Test
ollama run llama3.1:70b "Create architecture for e-commerce site"
```

**File:** `agents/cerebronn/cerebronn_local.py`

```python
#!/usr/bin/env python3
"""
Cerebronn Local - Uses Ollama for reasoning
"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import requests
import json
from pathlib import Path
from datetime import datetime
from agent_base import AgentBase, Task, Result


class CerebronnLocal(AgentBase):
    """
    Local reasoning agent using Ollama
    """
    
    def __init__(self):
        super().__init__('cerebronn', {
            'poll_interval': 60,
            'use_database': True
        })
        
        self.ollama_url = 'http://localhost:11434/api/generate'
        self.model = 'llama3.1:70b'
    
    def execute(self, task: Task) -> Result:
        if task.type == 'ARCHITECTURE_DESIGN':
            return self.design_architecture(task.data)
        elif task.type == 'COMPLEX_ANALYSIS':
            return self.analyze(task.data)
        elif task.type == 'CODE_REVIEW':
            return self.review_code(task.data)
        return Result(task.id, False, f"Unknown: {task.type}")
    
    def design_architecture(self, data):
        """Design system architecture"""
        requirements = data.get('requirements', [])
        constraints = data.get('constraints', [])
        
        prompt = f"""You are a senior software architect.

Design a system architecture for the following:

Requirements:
{chr(10).join(f'- {r}' for r in requirements)}

Constraints:
{chr(10).join(f'- {c}' for c in constraints)}

Provide:
1. High-level architecture overview
2. Component breakdown
3. Data flow
4. Technology recommendations
5. Implementation phases

Be specific and technical."""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=300  # 5 minutes for complex reasoning
            )
            
            if response.status_code == 200:
                result = response.json()
                architecture = result.get('response', '')
                
                return Result(
                    'architecture',
                    True,
                    {
                        'architecture': architecture,
                        'model': self.model,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            else:
                return Result('architecture', False, f"Ollama error: {response.status_code}")
                
        except Exception as e:
            return Result('architecture', False, str(e))
    
    def analyze(self, data):
        """Complex analysis"""
        topic = data.get('topic', '')
        context = data.get('context', '')
        
        prompt = f"""Analyze the following topic in detail:

Topic: {topic}

Context:
{context}

Provide comprehensive analysis including:
- Key insights
- Risks and considerations
- Recommendations
- Next steps"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                return Result(
                    'analysis',
                    True,
                    {'analysis': result.get('response', '')}
                )
            else:
                return Result('analysis', False, f"Error: {response.status_code}")
                
        except Exception as e:
            return Result('analysis', False, str(e))


if __name__ == '__main__':
    agent = CerebronnLocal()
    agent.run()
```

### Option C: Hybrid Approach (Recommended)

**CHAD_YI does simple reasoning** → **Escalate complex to cloud API**

```python
# In CHAD_YI
def handle_complex_task(self, task):
    """Route complex tasks appropriately"""
    
    # Simple tasks: Handle directly
    if task.complexity == 'simple':
        return self.solve_simple(task)
    
    # Medium tasks: Try local first
    if task.complexity == 'medium':
        result = self.try_local_reasoning(task)
        if result.success:
            return result
        # Fall back to cloud
    
    # Complex tasks: Use cloud API
    return self.escalate_to_cloud(task)
```

---

# INTEGRATION: CHAD_YI → Helios → Dashboard → Cerebronn

## Complete Flow

```
1. CHAD_YI (Monitor)
   └── Checks Helios status every 5 min
   └── Reports to you if issues
   └── You respond with actions

2. Helios (Sync)
   └── Reads ACTIVE.md every 15 min
   └── Updates data.json
   └── Pushes to git
   └── Reports success/failure to CHAD_YI

3. Dashboard (Display)
   └── Auto-refreshes every 15 min
   └── Shows current status
   └── Alerts on stale data

4. Cerebronn (Reasoning)
   └── Handles complex architecture tasks
   └── Provides detailed analysis
   └── Works asynchronously (slow)
```

## Status Commands

```bash
# Check entire flow
alias check-flow='
echo "=== CHAD_YI ===" && \
ls -la agents/chad-yi/outbox/*.md 2>/dev/null | tail -5 && \
echo "" && \
echo "=== HELIOS ===" && \
systemctl --user is-active helios && \
journalctl --user -u helios --since "1 hour ago" --no-pager | tail -5 && \
echo "" && \
echo "=== DASHBOARD ===" && \
ls -la mission-control-dashboard/data.json && \
cat mission-control-dashboard/data.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"Updated: {d.get('lastUpdated', 'unknown')}\")" && \
echo "" && \
echo "=== CEREBRONN ===" && \
pgrep -f cerebronn && echo "Running" || echo "Not running"'
```

**File Location:** `/home/chad-yi/.openclaw/workspace/FOCUSED_IMPLEMENTATION.md`

**Ready to implement. Fix the flow first, then expand.**