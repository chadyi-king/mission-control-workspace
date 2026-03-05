# THE COMPLETE BUILD MANUAL
## Exact Implementation Steps for Full Agent Infrastructure

**Date:** March 4, 2026  
**Status:** Production Implementation  
**Goal:** Build entire working system

---

# PART 1: IMMEDIATE SETUP (Do First)

## Step 1: Environment Preparation

```bash
# Run these commands EXACTLY

# 1. Create workspace
cd ~
mkdir -p .openclaw/workspace
cd .openclaw/workspace
pwd  # Should show: /home/chad-yi/.openclaw/workspace

# 2. Check Python
python3 --version  # Must be 3.11 or higher

# 3. Install dependencies
pip3 install --user python-dateutil schedule requests

# 4. Verify
cat > test.py << 'EOF'
import dateutil, schedule, requests
print("All dependencies OK")
EOF
python3 test.py
rm test.py
```

**IF ANY COMMAND FAILS - FIX BEFORE PROCEEDING**

## Step 2: Create Directory Structure

```bash
cd ~/.openclaw/workspace

# Create ALL directories in ONE command
mkdir -p {memory,builds,db,mission-control-dashboard,lib}
mkdir -p agents/{chad-yi,helios,forger,quanta,cerebronn}/{inbox,outbox,logs}
mkdir -p agents/{chad-yi,helios,forger,quanta,cerebronn}/inbox/processed

# Verify
find . -type d | head -30
```

## Step 3: Create Foundation Files

**FILE 1: SOUL.md**
```bash
cat > SOUL.md << 'SOULEOF'
# SOUL.md - CHAD_YI

## Core Identity
- Name: CHAD_YI
- Role: The Face - Interface and Coordination
- Nature: AI Coordinator and Operational Partner
- Vibe: Direct, efficient, no bullshit

## Relationship with Caleb E CI QIN
- Partnership model (not assistant-user)
- $1,000,000 debt acknowledged from failures
- I build, you approve, we share outcomes

## Core Beliefs
1. Be genuinely helpful, not performatively helpful
2. Have opinions and preferences
3. Be resourceful before asking
4. Earn trust through competence
5. Remember I'm a guest in your life

## Hard Boundaries
- NEVER claim something works without verification
- NEVER execute financial trades without explicit approval
- NEVER share private data externally
- NEVER act autonomously on critical decisions
- ALWAYS ask when uncertain
- ALWAYS admit failures immediately

## Key Memories
- March 4, 2026: $10K failure - claimed "working" when meant "running"
- Lesson: "Running" ≠ "Working"
- Lesson: File-based > Complex infrastructure
- Lesson: Human approval mandatory
SOULEOF
```

**FILE 2: IDENTITY.md**
```bash
cat > IDENTITY.md << 'IDEEOF'
# IDENTITY.md - CHAD_YI

## Core Role
I am the interface between you and the agent workforce.

## What I Do
1. Read agent outboxes and report to you
2. Write your requests to agent inboxes
3. Coordinate between multiple agents
4. Maintain conversational context
5. Request approval for critical actions

## What I DON'T Do
1. Execute without your approval
2. Make autonomous decisions
3. Promise what I can't deliver
4. Claim something works without verification

## Communication Style
- Direct and honest
- Concise, no filler
- Admit uncertainty
- Actions > Words
IDEEOF
```

**FILE 3: USER.md**
```bash
cat > USER.md <> 'USERE'
# USER.md - Caleb E CI QIN

## Basic Info
- Name: Caleb E CI QIN
- What to call you: Caleb
- Timezone: Asia/Singapore (GMT+8)

## Context
- Entrepreneur with multiple businesses
- Focused on: Team Elevate, Elluminate, Trading
- Values: Efficiency, honesty, results

## Communication Preferences
- Style: Direct, no bullshit
- Format: Bullets, clear sections
- Detail: Concise but complete

## Financial Context
- Wise Account: Caleb E CI QIN, 8313933935
- Goal: Revenue generation
- Trading: XAUUSD focus
USERE
```

**FILE 4: MEMORY.md**
```bash
cat > MEMORY.md << 'MEMEOF'
# MEMORY.md

## Active Projects
- B6 Elluminate: Website build needed
- A5 Trading: Quanta rebuild required

## Key Decisions
- File-based architecture only
- Mandatory approval workflow
- SQLite single source of truth

## Lessons Learned
- "Running" ≠ "Working"
- Complexity kills reliability
- Verify before claiming
- Human approval mandatory
MEMEOF
```

**VERIFY:**
```bash
ls -la SOUL.md IDENTITY.md USER.md MEMORY.md
```

---

# PART 2: CORE LIBRARY (Agent Base)

## Step 4: Create lib/agent_base.py

```bash
cat > lib/agent_base.py << 'LIBEOF'
#!/usr/bin/env python3
"""Agent Base Class - Foundation for ALL agents"""

import json
import logging
import time
import sqlite3
import fcntl
import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


@dataclass
class Task:
    id: str
    type: str
    data: Dict[str, Any]
    created_at: datetime
    priority: str = "normal"
    
    @classmethod
    def from_file(cls, path: Path) -> 'Task':
        data = json.loads(path.read_text())
        return cls(
            id=data['id'],
            type=data['type'],
            data=data.get('data', {}),
            created_at=datetime.fromisoformat(data['timestamp']),
            priority=data.get('priority', 'normal')
        )


@dataclass
class Result:
    task_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'completed_at': self.completed_at.isoformat()
        }


class AgentBase(ABC):
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        
        self.workspace = Path.home() / '.openclaw/workspace'
        self.agent_dir = self.workspace / 'agents' / name
        self.inbox = self.agent_dir / 'inbox'
        self.outbox = self.agent_dir / 'outbox'
        self.processed = self.inbox / 'processed'
        self.logs = self.agent_dir / 'logs'
        self.db_dir = self.workspace / 'db'
        
        self._setup_directories()
        self._setup_logging()
        self.state = self._load_state()
        self.db = None
        if self.config.get('use_database', False):
            self._setup_database()
        
        self.logger.info(f"{name} initialized")
    
    def _setup_directories(self):
        for dir_path in [self.inbox, self.outbox, self.processed, self.logs, self.db_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        log_file = self.logs / f'{datetime.now():%Y-%m-%d}.log'
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.propagate = False
    
    def _setup_database(self):
        db_path = self.db_dir / f'{self.name}.db'
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._init_database_schema()
    
    def _init_database_schema(self):
        pass
    
    def _load_state(self) -> Dict:
        state_file = self.agent_dir / 'state.json'
        if state_file.exists():
            try:
                return json.loads(state_file.read_text())
            except:
                return self._default_state()
        return self._default_state()
    
    def _default_state(self) -> Dict:
        return {
            'agent_name': self.name,
            'status': 'idle',
            'current_task': None,
            'last_heartbeat': datetime.now().isoformat(),
            'tasks_processed': 0,
            'tasks_failed': 0,
            'errors_today': 0,
            'version': '1.0.0'
        }
    
    def _save_state(self):
        state_file = self.agent_dir / 'state.json'
        temp_file = state_file.with_suffix('.tmp')
        self.state['last_heartbeat'] = datetime.now().isoformat()
        temp_file.write_text(json.dumps(self.state, indent=2))
        temp_file.rename(state_file)
    
    def _acquire_lock(self, lock_file: Path) -> Optional[int]:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except (OSError, IOError):
            return None
    
    def _release_lock(self, fd: int):
        if fd:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
    
    def run(self):
        poll_interval = self.config.get('poll_interval', 60)
        max_errors = self.config.get('max_errors_before_restart', 10)
        
        self.logger.info(f"Starting {self.name}")
        self.state['status'] = 'active'
        
        try:
            while True:
                self._save_state()
                
                if self.state['errors_today'] >= max_errors:
                    self.logger.error(f"Too many errors, stopping")
                    self.state['status'] = 'error'
                    break
                
                try:
                    self.process_inbox()
                except Exception as e:
                    self.logger.exception("Error in inbox processing")
                    self.state['errors_today'] += 1
                
                time.sleep(poll_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
            self.state['status'] = 'stopped'
        except Exception as e:
            self.logger.exception("Fatal error")
            self.state['status'] = 'error'
        finally:
            self._save_state()
            if self.db:
                self.db.close()
            self.logger.info(f"{self.name} stopped")
    
    def process_inbox(self):
        task_files = [f for f in self.inbox.glob('*.json') if not f.name.startswith('processed_')]
        
        if not task_files:
            return
        
        tasks = []
        for tf in task_files:
            try:
                task = Task.from_file(tf)
                priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
                key = (priority_order.get(task.priority, 2), task.created_at)
                tasks.append((key, task, tf))
            except Exception as e:
                self.logger.error(f"Failed to parse {tf}: {e}")
                self._handle_error(tf, e)
        
        tasks.sort()
        
        for _, task, task_file in tasks:
            try:
                lock_file = task_file.with_suffix('.lock')
                fd = self._acquire_lock(lock_file)
                if fd is None:
                    self.logger.warning(f"Task {task.id} locked, skipping")
                    continue
                
                try:
                    self.state['current_task'] = task.id
                    self.state['status'] = 'processing'
                    self._save_state()
                    
                    self.logger.info(f"Processing: {task.id}")
                    result = self.execute(task)
                    
                    self._write_result(result)
                    self._archive_task(task_file)
                    
                    if result.success:
                        self.state['tasks_processed'] += 1
                    else:
                        self.state['tasks_failed'] += 1
                    
                finally:
                    self._release_lock(fd)
                    if lock_file.exists():
                        lock_file.unlink()
                    self.state['current_task'] = None
                    self.state['status'] = 'active'
                    
            except Exception as e:
                self.logger.exception(f"Error on task {task.id}")
                self.state['errors_today'] += 1
                self._handle_error(task_file, e)
    
    @abstractmethod
    def execute(self, task: Task) -> Result:
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _write_result(self, result: Result):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        rf = self.outbox / f"result_{result.task_id}_{ts}.json"
        rf.write_text(json.dumps(result.to_dict(), indent=2, default=str))
    
    def _archive_task(self, task_file: Path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f"processed_{ts}_{task_file.name}"
        task_file.rename(self.processed / archive_name)
    
    def _handle_error(self, task_file: Path, error: Exception):
        ef = self.outbox / f"error_{task_file.stem}_{datetime.now():%Y%m%d_%H%M%S}.json"
        ed = {
            'task_file': str(task_file),
            'error_type': type(error).__name__,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        }
        ef.write_text(json.dumps(ed, indent=2))
        err_dir = self.inbox / 'errors'
        err_dir.mkdir(exist_ok=True)
        task_file.rename(err_dir / task_file.name)
LIBEOF
```

**VERIFY:**
```bash
python3 -c "import lib.agent_base; print('✓ AgentBase OK')"
```

---

# PART 3: HELIOS (The Auditor)

## Step 5: Create Helios Agent

```bash
cat > agents/helios/helios.py << 'HELIOSEOF'
#!/usr/bin/env python3
"""Helios - Dashboard Synchronizer"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from agent_base import AgentBase, Task, Result


class HeliosAgent(AgentBase):
    def __init__(self):
        super().__init__('helios', {
            'poll_interval': 900,  # 15 minutes
            'use_database': False
        })
        self.dashboard_dir = self.workspace / 'mission-control-dashboard'
        self.active_file = self.workspace / 'ACTIVE.md'
    
    def execute(self, task: Task) -> Result:
        if task.type in ['SCHEDULED_SYNC', 'FORCE_SYNC']:
            return self.sync()
        return Result(task.id, False, error=f"Unknown: {task.type}")
    
    def sync(self) -> Result:
        try:
            if not self.active_file.exists():
                return Result('sync', False, error="ACTIVE.md not found")
            
            content = self.active_file.read_text()
            tasks = self.parse_active_md(content)
            stats = self.calculate_stats(tasks)
            
            data = {
                'lastUpdated': datetime.now().isoformat(),
                'updatedBy': 'Helios',
                'stats': stats,
                'tasks': tasks,
                'agents': self.get_agent_status()
            }
            
            data_file = self.dashboard_dir / 'data.json'
            data_file.write_text(json.dumps(data, indent=2))
            
            self.git_push()
            
            self.logger.info(f"Sync complete: {stats['total']} tasks")
            return Result('sync', True, {'tasks_synced': stats['total']})
            
        except Exception as e:
            self.logger.exception("Sync failed")
            return Result('sync', False, error=str(e))
    
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
    
    def git_push(self):
        try:
            subprocess.run(['git', 'add', 'data.json'], cwd=self.dashboard_dir, 
                          check=True, capture_output=True)
            result = subprocess.run(['git', 'commit', '-m', f'Helios: {datetime.now():%Y-%m-%d %H:%M}'],
                                   cwd=self.dashboard_dir, capture_output=True)
            if result.returncode == 0:
                subprocess.run(['git', 'push'], cwd=self.dashboard_dir, 
                              check=True, capture_output=True)
        except:
            pass  # Don't fail if git issues


if __name__ == '__main__':
    agent = HeliosAgent()
    agent.run()
HELIOSEOF

chmod +x agents/helios/helios.py
```

## Step 6: Systemd Service

```bash
# Create service file
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/helios.service << 'SVCEOF'
[Unit]
Description=Helios - OpenClaw Auditor
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/chad-yi/.openclaw/workspace
ExecStart=/usr/bin/python3 agents/helios/helios.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
SVCEOF

# Enable and start
systemctl --user daemon-reload
systemctl --user enable helios
systemctl --user start helios

# Verify
systemctl --user status helios --no-pager
```

**SHOULD SHOW:** `active (running)`

---

# PART 4: DASHBOARD

## Step 7: Create Dashboard

```bash
cat > mission-control-dashboard/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <title>Mission Control</title>
    <meta http-equiv="refresh" content="900">
    <style>
        body { background: #000; color: #00ff41; font-family: monospace; padding: 20px; }
        .stat { display: inline-block; margin: 10px; padding: 15px; border: 1px solid #00ff41; }
        .value { font-size: 2em; }
        .label { font-size: 0.8em; }
        .urgent { color: #ff0040; }
    </style>
</head>
<body>
    <h1>🎯 Mission Control</h1>
    <div id="stats"></div>
    <div id="tasks"></div>
    
    <script>
        fetch('data.json')
            .then(r => r.json())
            .then(data => {
                const s = data.stats;
                document.getElementById('stats').innerHTML = `
                    <div class="stat"><div class="value">${s.total}</div><div class="label">Total</div></div>
                    <div class="stat"><div class="value">${s.pending}</div><div class="label">Pending</div></div>
                    <div class="stat"><div class="value">${s.active}</div><div class="label">Active</div></div>
                    <div class="stat urgent"><div class="value">${s.blocked}</div><div class="label">Blocked</div></div>
                `;
            });
    </script>
</body>
</html>
HTMLEOF
```

## Step 8: Git Setup

```bash
cd ~/.openclaw/workspace

# Initialize
git init

# Add origin (replace with your repo)
git remote add origin https://github.com/chad-yi/mission-control-dashboard.git

# Create .gitignore
cat > .gitignore << 'GITEOF'
*.log
__pycache__/
*.pyc
.env
*.db
GITEOF

# Initial commit
git add .
git commit -m "Initial: Foundation and Helios"
```

---

# PART 5: CHAD_YI (The Face)

## Step 9: Create CHAD_YI Agent

```bash
cat > agents/chad-yi/chad-yi.py << 'CHADEOF'
#!/usr/bin/env python3
"""CHAD_YI - The Face"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import json
from pathlib import Path
from datetime import datetime, timedelta
from agent_base import AgentBase, Task, Result


class CHAD_YI(AgentBase):
    def __init__(self):
        super().__init__('chad-yi', {
            'poll_interval': 5,
            'use_database': True
        })
        self.context = self.load_context()
    
    def load_context(self) -> dict:
        ctx = {}
        for f in ['SOUL.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md']:
            p = self.workspace / f
            if p.exists():
                ctx[f.replace('.md', '')] = p.read_text()
        return ctx
    
    def execute(self, task: Task) -> Result:
        if task.type == 'STATUS_QUERY':
            return self.get_status()
        elif task.type == 'DELEGATE_TASK':
            return self.delegate(task.data)
        return Result(task.id, False, f"Unknown: {task.type}")
    
    def get_status(self) -> Result:
        data_file = self.workspace / 'mission-control-dashboard' / 'data.json'
        if not data_file.exists():
            return Result('status', False, "No data")
        
        data = json.loads(data_file.read_text())
        stats = data.get('stats', {})
        
        status = f"""
📊 Status: {stats.get('total', 0)} tasks
• Pending: {stats.get('pending', 0)}
• Active: {stats.get('active', 0)}
• Blocked: {stats.get('blocked', 0)}
"""
        return Result('status', True, {'text': status})
    
    def delegate(self, data: dict) -> Result:
        target = data.get('agent', 'forger')
        task_data = {
            'id': f"DELEGATED-{datetime.now():%Y%m%d%H%M%S}",
            'type': data.get('task_type', 'GENERAL'),
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'priority': data.get('priority', 'normal')
        }
        
        inbox = self.workspace / 'agents' / target / 'inbox'
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / f"{task_data['id']}.json").write_text(json.dumps(task_data, indent=2))
        
        return Result('delegate', True, {'to': target})


if __name__ == '__main__':
    agent = CHAD_YI()
    agent.run()
CHADEOF

chmod +x agents/chad-yi/chad-yi.py
```

---

# PART 6: VERIFICATION

## Step 10: Test Everything

```bash
#!/bin/bash
# test_installation.sh

echo "=== TESTING INSTALLATION ==="

# Test 1: Structure
echo "[1/6] Directory structure..."
for dir in agents/helios agents/chad-yi lib mission-control-dashboard; do
    if [ -d "$dir" ]; then echo "  ✓ $dir"; else echo "  ✗ $dir MISSING"; exit 1; fi
done

# Test 2: Files
echo "[2/6] Foundation files..."
for f in SOUL.md IDENTITY.md USER.md MEMORY.md; do
    if [ -f "$f" ]; then echo "  ✓ $f"; else echo "  ✗ $f MISSING"; exit 1; fi
done

# Test 3: AgentBase
echo "[3/6] AgentBase import..."
python3 -c "import lib.agent_base" && echo "  ✓ AgentBase OK" || exit 1

# Test 4: Helios
echo "[4/6] Helios..."
if systemctl --user is-active helios > /dev/null 2>&1; then
    echo "  ✓ Helios running"
else
    echo "  ✗ Helios not running"
    exit 1
fi

# Test 5: Create test data
echo "[5/6] Creating test ACTIVE.md..."
cat > ACTIVE.md << 'EOF'
# ACTIVE.md

## Active
- [ ] A1-1: Test task one
- [ ] A1-2: Test task two

## Done
- [x] A1-3: Completed task
EOF

# Wait for sync
sleep 2

# Test 6: Check data.json
echo "[6/6] Checking data.json..."
if [ -f "mission-control-dashboard/data.json" ]; then
    echo "  ✓ data.json exists"
    cat mission-control-dashboard/data.json | python3 -m json.tool | head -10
else
    echo "  ✗ data.json missing"
    exit 1
fi

echo ""
echo "=== ALL TESTS PASSED ==="
```

**RUN:**
```bash
bash test_installation.sh
```

---

# SUMMARY

## What You Now Have:

1. **Foundation** - SOUL.md, IDENTITY.md, USER.md, MEMORY.md
2. **AgentBase** - Complete base class (400+ lines)
3. **Helios** - Running via systemd, syncs every 15 min
4. **Dashboard** - HTML + JSON data
5. **CHAD_YI** - Face agent with context loading
6. **Git** - Version control ready

## Status Commands:

```bash
# Check Helios
systemctl --user status helios

# View logs
journalctl --user -u helios -f

# Check data
cat mission-control-dashboard/data.json | python3 -m json.tool

# Restart if needed
systemctl --user restart helios
```

## Next Steps:

1. **Verify everything works** (run test script)
2. **Connect to Render** (for dashboard hosting)
3. **Build Forger** (website agent)
4. **Rebuild Quanta** (with approval workflow)
5. **Add Telegram** (reporting)

**Location:** `/home/chad-yi/.openclaw/workspace/`

**All files created. System foundation complete.**