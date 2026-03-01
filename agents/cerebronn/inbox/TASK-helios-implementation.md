## Task: Implement Helios Agent Coordination System

**Priority:** HIGH  
**Context:** Helios is documented to coordinate all agents but the code isn't fully implemented. The architecture is designed, now it needs to be built.

---

## Current State

**Helios IS running:**
- Process: `helios-v2.py` (PID 1447358)
- Systemd service: `/etc/systemd/system/helios.service`
- Cron: Every 15 min heartbeat

**Location:** `/home/chad-yi/.openclaw/workspace/agents/helios/`

**Existing files:**
- `helios-v2.py` — Main audit script (running)
- `helios-audit.py` — Possibly old version
- `SOUL.md`, `IDENTITY.md`, `LEARNING.md`, `OPERATIONS.md` — Documentation

---

## What Needs To Be Implemented

### 1. Helios Agent Coordination (helios-v2.py)

**Add to the 15-minute audit cycle:**

```python
# During each audit cycle, Helios should:

def coordinate_agents():
    agents = ['escritor', 'quanta', 'forger', 'autour', 'mensamusa', 'tele']
    
    for agent_name in agents:
        # Check if agent needs poking
        status = check_agent_status(agent_name)
        inbox_pending = check_inbox_pending(agent_name)
        last_response = get_last_response_time(agent_name)
        
        # Decision: Poke or not?
        if inbox_pending and status == 'idle':
            poke_agent(agent_name, reason='new_task')
        elif last_response > 24h and status == 'active':
            poke_agent(agent_name, reason='stale_check')
        elif not_responded_to_previous_poll(agent_name):
            poke_agent(agent_name, reason='follow_up')

def poke_agent(agent_name, reason):
    """Wake up an agent to check their inbox"""
    # Try systemd first
    result = subprocess.run(['systemctl', 'start', agent_name], capture_output=True)
    if result.returncode == 0:
        log(f"Poked {agent_name} via systemd")
        return
    
    # Fallback: Run agent script directly
    script_path = f'/home/chad-yi/.openclaw/workspace/agents/{agent_name}/{agent_name}-agent.py'
    if os.path.exists(script_path):
        subprocess.Popen(['python3', script_path, '--check-inbox'])
        log(f"Poked {agent_name} via script")
        return
    
    # Last resort: Write poke file
    write_poke_file(agent_name, reason)
    log(f"Poked {agent_name} via file")
```

**Key behaviors:**
- Poll every agent every 15 minutes
- Detect when agents need to wake up (new tasks, stale status, unresponsive)
- Poke via: systemd → script → file (in that order)
- Track response times
- Escalate to CHAD_YI if unresponsive after 3 cycles

### 2. Agent Scripts (Template for each agent)

Each agent needs a script at `agents/{name}/{name}-agent.py`:

```python
#!/usr/bin/env python3
"""
{AgentName} Agent
Wakes up when poked by Helios, checks inbox, processes work, sleeps.
"""

import os
import json
import sys
from datetime import datetime

AGENT_NAME = '{agent_name}'
BASE_DIR = '/home/chad-yi/.openclaw/workspace/agents'
INBOX_DIR = f'{BASE_DIR}/{AGENT_NAME}/inbox'
OUTBOX_DIR = f'{BASE_DIR}/{AGENT_NAME}/outbox'
HELIOS_INBOX = f'{BASE_DIR}/helios/inbox'

def read_inbox():
    """Read all pending messages from inbox"""
    messages = []
    for filename in os.listdir(INBOX_DIR):
        if filename.endswith('.json'):
            with open(f'{INBOX_DIR}/{filename}') as f:
                messages.append(json.load(f))
    return messages

def handle_poke(message):
    """Handle poke from Helios"""
    reason = message.get('reason')
    
    if reason == 'new_task':
        task = find_new_task()
        acknowledge_task(task)
        process_task(task)
    elif reason == 'status_check':
        report_status()
    elif reason == 'stale_check':
        explain_idle_status()

def acknowledge_task(task):
    """Tell Helios we received the task"""
    response = {
        'from': AGENT_NAME,
        'to': 'helios',
        'type': 'task_acknowledged',
        'task_id': task['id'],
        'timestamp': datetime.now().isoformat()
    }
    write_to_helios_inbox(response)

def report_status():
    """Report current status to Helios"""
    status = read_state_json()
    response = {
        'from': AGENT_NAME,
        'to': 'helios',
        'type': 'status_response',
        'status': status.get('status'),
        'current_task': status.get('current_task'),
        'progress': get_progress(),
        'timestamp': datetime.now().isoformat()
    }
    write_to_helios_inbox(response)

def write_to_helios_inbox(message):
    """Write response to Helios inbox"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = f'{HELIOS_INBOX}/{AGENT_NAME}-response-{timestamp}.json'
    with open(filename, 'w') as f:
        json.dump(message, f, indent=2)

def update_state(status, current_task=None):
    """Update state.json"""
    state_file = f'{BASE_DIR}/{AGENT_NAME}/state.json'
    state = {'status': status, 'current_task': current_task, 'lastActivity': datetime.now().isoformat()}
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def main():
    if '--check-inbox' in sys.argv:
        # Wake up, check inbox, process, sleep
        messages = read_inbox()
        for msg in messages:
            if msg.get('from') == 'helios' and msg.get('type') == 'poke':
                handle_poke(msg)
        
        # Update state to show we checked in
        update_state('idle' if not has_work() else 'active')
        
        # Exit (go back to sleep)
        sys.exit(0)
    
    # If run without args, just report status
    report_status()

if __name__ == '__main__':
    main()
```

**Build this template first, then customize for:**
- `agents/escritor/escritor-agent.py` — Story writing agent
- `agents/quanta/quanta-agent.py` — Trading agent
- `agents/forger/forger-agent.py` — Web dev agent

### 3. CHAD_YI 2-Hour Heartbeat Cron

Create `/home/chad-yi/.openclaw/workspace/agents/chad-yi/chad-yi-cron.py`:

```python
#!/usr/bin/env python3
"""
CHAD_YI 2-Hour Heartbeat
Sends proactive status updates to Caleb.
"""

import json
import subprocess
from datetime import datetime

def get_dashboard_status():
    """Read data.json and summarize"""
    with open('/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json') as f:
        data = json.load(f)
    
    return {
        'total_tasks': data['stats']['total'],
        'pending': data['stats']['pending'],
        'active': data['stats']['active'],
        'urgent': [t for t in data['tasks'].values() if is_urgent(t)]
    }

def check_helios_reports():
    """Check recent Helios reports"""
    # Read last few audit reports from helios/outbox/
    # Return summary of issues found
    pass

def send_heartbeat():
    """Send status report to Caleb"""
    dashboard = get_dashboard_status()
    helios_summary = check_helios_reports()
    
    message = f"""
Heartbeat - {datetime.now().strftime('%H:%M')} SGT:
• Dashboard: {dashboard['total_tasks']} tasks | {dashboard['pending']} pending | {dashboard['active']} active
• Urgent: {len(dashboard['urgent'])} items need attention
• Helios: Last audit clean
"""
    
    # Send via Telegram (using existing messaging)
    # Or write to a file that CHAD_YI main process picks up
    print(message)

if __name__ == '__main__':
    send_heartbeat()
```

**Add cron job:**
```bash
# Add to crontab
0 */2 * * * /home/chad-yi/.venv/bin/python /home/chad-yi/.openclaw/workspace/agents/chad-yi/chad-yi-cron.py >> /tmp/chad-yi-cron.log 2>&1
```

---

## Deliverables

1. **Updated helios-v2.py** with agent coordination + poke functionality
2. **Agent script template** at `agents/_templates/agent-script.py`
3. **Escritor agent** at `agents/escritor/escritor-agent.py`
4. **CHAD_YI cron script** at `agents/chad-yi/chad-yi-cron.py`
5. **Test plan:** How to verify the coordination works

---

## Testing Checklist

```bash
# 1. Verify Helios still runs after changes
sudo systemctl restart helios
sudo systemctl status helios

# 2. Test agent poke
python3 agents/escritor/escritor-agent.py --check-inbox
# Should read inbox, report status, exit

# 3. Write test poke to escritor inbox
echo '{"from":"helios","type":"poke","reason":"test"}' > agents/escritor/inbox/test.json

# 4. Trigger Helios audit (or wait 15 min)
# Should detect poke needed and trigger agent

# 5. Verify response in helios inbox
ls agents/helios/inbox/escritor-response-*
```

---

## Reference Documentation

Read these files for context:
- `/home/chad-yi/.openclaw/workspace/agents/helios/OPERATIONS.md` — Section "Agent Coordination (My COO Role)"
- `/home/chad-yi/.openclaw/workspace/agents/AGENT_PROTOCOL.md` — How agents should work
- `/home/chad-yi/.openclaw/workspace/agents/escritor/SKILL.md` — What Escritor does

---

**Success criteria:**
- [ ] Helios pokes agents every 15 min
- [ ] Agents wake up, check inbox, report status
- [ ] CHAD_YI gets 2-hour heartbeat
- [ ] Dashboard updates reflect agent responses

**File this task:** Write to `agents/cerebronn/inbox/TASK-helios-implementation.md`
