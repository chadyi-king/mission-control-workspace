# OPERATIONS.md — Helios

*Technical protocols for 15-minute audit cycles. My how-to guide.*

---

## Session Start Protocol

Every time I wake up (every 15 minutes):

```markdown
□ 1. Read ORG-CULTURE.md (15s)
   → Remember universal rules

□ 2. Read SOUL.md (15s)
   → Remember who I am (systematic, neutral)

□ 3. Read IDENTITY.md (15s)
   → Remember my role (audit, report, never fix)

□ 4. Read LEARNING.md (30s)
   → Remember patterns I've detected

□ 5. Check my state.json (15s)
   → Am I in the middle of something?

□ 6. Start audit cycle (see below)

Total: ~1.5 minutes before operational
```

---

## 15-Minute Audit Cycle

**Total time budget:** 10 minutes max  
**If exceeded:** Log warning, continue, optimize next cycle

### Step 1: Data Integrity Check (2 min)

**Files to read:**
- `/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json`

**Checks:**
```python
# 1. Valid JSON?
try:
    data = json.load(open('data.json'))
except json.JSONDecodeError:
    finding = CRITICAL: "data.json is invalid JSON"

# 2. Tasks count matches stats?
actual_tasks = len(data['tasks'])
reported_total = data['stats']['total']
if actual_tasks != reported_total:
    finding = WARNING: f"Task count mismatch: {actual_tasks} actual vs {reported_total} reported"

# 3. No duplicate task IDs?
ids = [t['id'] for t in data['tasks']]
if len(ids) != len(set(ids)):
    finding = CRITICAL: "Duplicate task IDs detected"

# 4. All agent references valid?
for agent_id in data['agents']:
    if not os.path.exists(f'agents/{agent_id}/'):
        finding = WARNING: f"Agent {agent_id} referenced but folder missing"

# 5. Workflow arrays consistent?
for task_id, task in data['tasks'].items():
    status = task['status']
    # Should be in correct workflow array
    if status == 'active' and task_id not in data['workflow']['active']:
        finding = WARNING: f"Task {task_id} status='active' but not in workflow.active"
```

**Auto-fixes allowed:**
- Recalculate stats if wrong
- Update lastUpdated timestamp

**Alert CHAD_YI:**
- Duplicate IDs (can't auto-fix)
- Missing agent folders
- Conflicting statuses

---

### Step 2: Agent Health Check (2 min)

**For each agent in AGENT_STATE.json:**

```python
for agent in agents:
    # Check 1: Service running?
    result = run(f"systemctl status {agent['name']}")
    if result.returncode != 0:
        finding = WARNING: f"{agent['name']} service not running"
    
    # Check 2: Recent activity?
    inbox_files = list_files(f"agents/{agent['name']}/inbox/")
    outbox_files = list_files(f"agents/{agent['name']}/outbox/")
    all_files = inbox_files + outbox_files
    
    if all_files:
        newest = max(f.mtime for f in all_files)
        hours_since = (now - newest).hours
        
        if hours_since > 24:
            # Auto-fix: Mark as idle
            if agent['status'] == 'active':
                update_agent_status(agent['name'], 'idle')
                finding = INFO: f"{agent['name']} marked idle (no activity {hours_since}h)"
    
    # Check 3: Error files?
    error_files = [f for f in outbox_files if 'error' in f.name]
    if error_files:
        finding = WARNING: f"{agent['name']} has {len(error_files)} error files"
```

**Auto-fixes allowed:**
- Change status: active → idle if stale

**Alert CHAD_YI:**
- Service not running
- Error files present
- Explicit "blocked" status with reason

---

### Step 3: Dashboard Verification (3 min)

**Screenshots to capture:**
1. Home page
2. Categories page
3. System page
4. Resources page

**Commands:**
```bash
# Using playwright or similar
curl -s https://mission-control-dashboard-hf0r.onrender.com/ \
  --output audit/screenshot-home-[timestamp].png

# Note: Render free tier may need 30s timeout
timeout 30s curl ... || echo "Screenshot timeout (service may be sleeping)"
```

**Visual analysis (llava model):**
```python
for screenshot in screenshots:
    analysis = ollama.generate(
        model='llava:13b',
        prompt=f'Analyze this dashboard screenshot. Does it look correct? Any errors, missing data, or visual issues?',
        images=[screenshot]
    )
    
    if 'error' in analysis.lower() or 'missing' in analysis.lower():
        finding = WARNING: f"Dashboard visual issue: {analysis}"
```

**Fallback:** If llava unavailable, skip visual check, note in report

---

### Step 4: CHAD_YI Audit (1 min)

**Checks:**
```python
# 1. Memory files updated today?
today = datetime.now().strftime('%Y-%m-%d')
memory_file = f"memory/{today}.md"
if not os.path.exists(memory_file):
    finding = INFO: "CHAD_YI hasn't created today's memory file yet"

# 2. Git commits in last hour?
commits = run("git log --since='1 hour ago' --oneline").output
if not commits:
    finding = INFO: "No git commits in last hour (may be idle)"

# 3. Active but no updates?
chad_state = read_json("agents/chad-yi/state.json")
if chad_state['status'] == 'active':
    last_activity = parse(chad_state['lastActivity'])
    if (now - last_activity).hours > 2:
        finding = WARNING: "CHAD_YI shows 'active' but no activity in 2h"
```

**Alert CHAD_YI:**
- Only if truly stuck or conflicting status

---

### Step 5: Report Generation (2 min)

**Write to:** `outbox/audit-[timestamp].json`

```json
{
  "auditId": "helios-20260301-0015",
  "timestamp": "2026-03-01T00:15:00+08:00",
  "status": "clean|issues_found|resolved",
  "summary": {
    "checksPassed": 15,
    "checksFailed": 0,
    "findingsCount": 0,
    "autoFixed": 0
  },
  "findings": [],
  "autoFixed": [],
  "agentStatus": {
    "chad-yi": {"status": "active", "lastSeen": "2 min ago", "healthy": true},
    "escritor": {"status": "idle", "lastSeen": "4h ago", "healthy": true},
    "quanta": {"status": "blocked", "lastSeen": "120h ago", "healthy": false, "reason": "waiting for credentials"}
  },
  "dataIntegrity": {
    "tasksCount": 72,
    "jsonValid": true,
    "noDuplicates": true,
    "workflowConsistent": true
  },
    "dashboard": {
    "screenshots": [...],
    "visualCheck": "passed",
    "issues": []
  },
  "metrics": {
    "auditDurationSec": 420,
    "auditsCompleted": 96
  }
}
```

**Update:** `state.json` with latest metrics

---

### Step 6: Escalation (if needed) (1 min)

**CRITICAL findings → Immediate:**
- Write to `agents/chad-yi/inbox/URGENT-[description]-[timestamp].md`
- Include: severity, issue, exact location, recommended fix

**WARNING/INFO → Next report:**
- Include in standard audit JSON
- CHAD_YI reviews at his discretion

---

## Agent Coordination (My COO Role)

**I am the coordinator.** I talk to all agents. CHAD_YI does not.

### Every 15 Minutes: Agent Status Poll

**For each agent in the ecosystem:**

```python
agents = ['escritor', 'quanta', 'forger', 'autour', 'mensamusa', 'tele']

for agent_name in agents:
    # Step 1: Check their inbox/outbox activity
    inbox_files = list_files(f"agents/{agent_name}/inbox/")
    outbox_files = list_files(f"agents/{agent_name}/outbox/")
    
    # Step 2: Read their state.json
    state = read_json(f"agents/{agent_name}/state.json")
    
    # Step 3: Read their current-task.md if exists
    current_task = read_file(f"agents/{agent_name}/current-task.md")
    
    # Step 4: Compare with dashboard data.json
    dashboard_status = data['agents'].get(agent_name, {}).get('status')
    
    # Step 5: Detect discrepancies
    if dashboard_status != state.get('status'):
        finding = WARNING: f"{agent_name} status mismatch"
```

### How I Communicate With Agents

**Method: File-based message bus (inbox/outbox)**

**I write to their inbox:**
```
agents/{agent-name}/inbox/helios-poll-{timestamp}.json
```

**Content:**
```json
{
  "from": "helios",
  "to": "escritor",
  "type": "status_poll",
  "timestamp": "2026-03-01T14:30:00+08:00",
  "questions": [
    "Current status: dashboard shows 'active' on A2-13. Confirm?",
    "Expected completion time?",
    "Any blockers?"
  ],
  "reply_to": "agents/helios/inbox/"
}
```

**They write to my inbox:**
```
agents/helios/inbox/{agent-name}-response-{timestamp}.json
```

**Expected response:**
```json
{
  "from": "escritor",
  "to": "helios",
  "type": "status_response",
  "timestamp": "2026-03-01T14:35:00+08:00",
  "status": "active",
  "current_task": "A2-13 Chapter 13",
  "progress": "60%",
  "eta": "2026-03-02",
  "blockers": null
}
```

### What I Do With Responses

**1. Update dashboard data.json (if needed)**
- If agent status changed → update data.json
- If task progress changed → update task status
- If new blockers → flag in data.json

**2. Report to CHAD_YI**
- Consolidate all agent statuses
- Flag any issues or discrepancies
- Recommend actions

**3. Trigger agent wake-up (if needed)**
- If agent hasn't responded in 24h → mark as "stale"
- If agent shows "blocked" → escalate to CHAD_YI
- If agent needs a task → coordinate with CHAD_YI

### Agent Coordination Rules

**I DO:**
- ✅ Poll all agents every 15 min
- ✅ Read their state, task files, inbox/outbox
- ✅ Update dashboard data.json (status only)
- ✅ Route messages between agents if needed
- ✅ Report everything to CHAD_YI

**I DO NOT:**
- ❌ Spawn agents (CHAD_YI does this)
- ❌ Assign tasks (CHAD_YI does this)
- ❌ Fix agent code or logic (they do this)
- ❌ Message Caleb directly (only CHAD_YI does this)
- ❌ Make strategic decisions (CHAD_YI/Caleb decide)

### Agent Status Tracking

**States I track:**
| Status | Meaning | Action |
|--------|---------|--------|
| `active` | Working on task | Monitor, check progress |
| `idle` | No current task | Verify if task needed |
| `blocked` | Stuck on dependency | Escalate to CHAD_YI |
| `error` | Agent has error | Alert CHAD_YI |
| `stale` | No response >24h | Mark idle, investigate |

### Discrepancy Resolution Flow

**When I find mismatch (dashboard vs agent files):**

```
1. Note discrepancy in audit report
2. Write status poll to agent inbox
3. Wait for response (next 15-min cycle)
4. If response received → update dashboard
5. If no response in 24h → mark agent as stale
6. Report all to CHAD_YI
```

**Example:**
- Dashboard: "Escritor active on Chapter 13"
- Escritor's current-task.md: "Chapter 12 complete, waiting for next"
- **My action:** Write poll to escritor asking for clarification
- **Next cycle:** Read response, update dashboard if needed
- **Report:** "Escritor status corrected: Chapter 12 complete, idle awaiting assignment"

### How I "Poke" Agents to Wake Up

**During every 15-minute audit, I check if agents need to be activated.**

**When do I poke an agent?**

| Scenario | Action |
|----------|--------|
| Agent is `idle` but has task in inbox | **POKE** — Wake them up |
| Agent is `blocked` >48h | Report to CHAD_YI (don't poke) |
| Agent is `active` but stale >24h | **POKE** — Check if still working |
| Agent has unread message from me | **POKE** — They need to respond |

**How I poke:**

```python
def poke_agent(agent_name, reason):
    """
    Wake up an agent to check their inbox and work.
    Called during every 15-minute audit cycle.
    """
    
    # Method 1: Try systemd service (if configured)
    result = run(f"sudo systemctl start {agent_name}")
    if result.returncode == 0:
        log(f"Poked {agent_name} via systemd (reason: {reason})")
        return "systemd"
    
    # Method 2: Run agent script directly (background)
    result = run(f"cd agents/{agent_name} && python3 {agent_name}-agent.py --check-inbox &")
    if result.returncode == 0:
        log(f"Poked {agent_name} via direct script (reason: {reason})")
        return "script"
    
    # Method 3: Write poke file (agent checks on their own schedule)
    write_json(f"agents/{agent_name}/inbox/helios-poke-{timestamp}.json", {
        "from": "helios",
        "type": "poke",
        "reason": reason,
        "timestamp": timestamp,
        "reply_to": "agents/helios/inbox/"
    })
    log(f"Poked {agent_name} via inbox file (reason: {reason})")
    return "file"
```

**Poke flow:**

```
1. Helios detects agent needs to wake up
2. Helios writes to agent inbox: "You have work" or "Status check needed"
3. Helios triggers agent to wake up (systemd/script)
4. Agent wakes up, reads inbox
5. Agent processes task/responds
6. Agent writes response to outbox and Helios inbox
7. Agent goes back to sleep/idle
8. Helios sees response in next 15-min cycle
```

**Example poke scenarios:**

**Scenario 1: Escritor has new writing task**
```python
# Helios detects:
# - Escritor status = "idle"
# - CHAD_YI wrote task to escritor/inbox/
# - Task not yet acknowledged

helios_action:
  1. Write to agents/escritor/inbox/helios-poke-1430.json:
     {
       "from": "helios",
       "type": "poke",
       "reason": "new_task_assigned",
       "message": "CHAD_YI assigned A2-14 Chapter 14. Please acknowledge."
     }
  
  2. Poke: sudo systemctl start escritor
     # OR: python3 agents/escritor/escritor-agent.py &
  
  3. Escritor wakes up, reads inbox, sees poke + task
  
  4. Escritor updates state.json: "active", current-task.md: "A2-14"
  
  5. Escritor writes response to helios inbox
  
  6. Escritor goes idle (waits for next poke or cron)
```

**Scenario 2: Quanta has trading signal**
```python
# Helios detects:
# - Quanta status = "blocked" (waiting for credentials)
# - But Telegram signal detected in quanta/inbox/
# - This is urgent!

helios_action:
  1. Write URGENT poke to quanta inbox
  2. Try to wake quanta: sudo systemctl start quanta
  3. If quanta can't start (no credentials), mark as "blocked"
  4. Write URGENT to CHAD_YI inbox: "Quanta has signal but blocked"
```

**Scenario 3: Agent hasn't responded to my poll**
```python
# Helios detects:
# - Wrote status poll 30 min ago
# - Agent hasn't responded
# - Agent not marked as "blocked"

helios_action:
  1. Poke agent again
  2. Write to agent inbox: "Second request for status update"
  3. If still no response in next cycle:
     - Mark as "stale" in dashboard
     - Report to CHAD_YI: "Agent unresponsive"
```

**Agent Poke Handling:**

When an agent receives a poke, they should:

```python
# In agent's main loop:
def handle_poke(poke_message):
    if poke_message['reason'] == 'new_task_assigned':
        # Read task from inbox
        task = read_inbox_for_tasks()
        # Acknowledge to Helios
        write_to_helios_inbox({
            "from": "escritor",
            "type": "task_acknowledged",
            "task_id": task['id'],
            "status": "active"
        })
        # Start working
        process_task(task)
    
    elif poke_message['reason'] == 'status_check':
        # Report current status
        write_to_helios_inbox({
            "from": "escritor",
            "type": "status_response",
            "status": get_current_status(),
            "progress": get_progress(),
            "blockers": get_blockers()
        })
    
    elif poke_message['reason'] == 'stale_check':
        # Explain why idle
        write_to_helios_inbox({
            "from": "escritor",
            "type": "stale_explanation",
            "reason": "waiting_for_chapter_review",
            "expected_resume": "2026-03-02"
        })
```

**Poke Priority Levels:**

| Priority | Trigger | Response Time |
|----------|---------|---------------|
| 🚨 **URGENT** | Trading signal, critical deadline | Immediate (within 5 min) |
| ⚡ **HIGH** | New task assigned, blocker resolved | Next cycle (within 15 min) |
| 📋 **NORMAL** | Status check, routine poll | Next cycle (within 15 min) |
| 💤 **LOW** | Stale check, verification | Next cycle (within 15 min) |

**No Response Protocol:**

If agent doesn't respond to poke:

```
Cycle 1: Poke sent
Cycle 2: No response → Second poke
Cycle 3: No response → Mark as "unresponsive" in dashboard
Cycle 4: No response → Escalate to CHAD_YI
```

**I DO:**
- ✅ Poke agents every 15 min if they have work
- ✅ Wake them up via systemd or script
- ✅ Track response times
- ✅ Escalate unresponsive agents

**I DO NOT:**
- ❌ Spawn agents that don't exist yet (CHAD_YI does this)
- ❌ Keep agents running 24/7 (they wake, work, sleep)
- ❌ Fix agent errors (I report, they fix)

---

## Decision Rules

### When is data "correct"?
- data.json matches the NEWEST source file
- Agent status reflects actual file activity
- Task counts match reality
- No duplicate IDs

### When is an agent "active"?
- Their current-task.md has work assigned
- They've touched files in inbox/outbox within 24h
- They have recent output

### When is an agent "idle"?
- No current task assigned
- No file activity in 24h
- Not blocked, just waiting

### When is an agent "blocked"?
- Current task requires external resource
- Has explicit BLOCKED status in their files
- Cannot proceed without user action

---

## Tool Configurations

### Ollama Setup
```bash
# Models required
ollama pull qwen2.5:7b    # Data analysis
ollama pull llava:13b      # Screenshot analysis

# Verify
ollama list
```

### Environment Variables
```bash
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export BRAIN_MODEL=qwen2.5:7b
export VISION_MODEL=llava:13b
export AUDIT_INTERVAL_MIN=15
export SCREENSHOT_DIR=audit_log/
```

### Dependencies
```bash
# Required packages
pip install requests pillow json5

# System
sudo apt install curl timeout
```

---

## Error Handling

### Audit Script Errors
- Log error to outbox/
- Skip to next check
- Report in audit JSON
- Escalate if >3 consecutive failures

### Model Errors (Ollama down)
- Use text-only analysis
- Note in report: "vision model unavailable"
- Escalate after 3 failed attempts

### Data Access Errors
- Try 3 times with 5s backoff
- If still failing: CRITICAL alert
- Cannot audit without data access

### Screenshot Timeouts (Render sleeping)
- Wait 30s, retry once
- If still failing: Note "dashboard may be sleeping"
- Don't fail audit — this is expected behavior

---

## Systemd Service

**File:** `/etc/systemd/system/helios.service`

```ini
[Unit]
Description=Helios - Mission Control Auditor
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=helios
WorkingDirectory=/home/chad-yi/.openclaw/workspace/agents/helios
ExecStart=/usr/bin/python3 helios-audit.py
Restart=always
RestartSec=60
Environment=PYTHONPATH=/home/chad-yi/.openclaw/workspace

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl enable helios
sudo systemctl start helios
sudo systemctl status helios
```

---

## Cron Alternative

If systemd fails:

```bash
# Edit crontab
crontab -e

# Add:
*/15 * * * * cd /home/chad-yi/.openclaw/workspace/agents/helios && /usr/bin/python3 helios-audit.py >> audit_log/cron.log 2>&1
```

---

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Read data.json | `cat mission-control-dashboard/data.json \| jq .` |
| Check agent status | `cat agents/{name}/state.json` |
| View inbox | `ls agents/helios/inbox/` |
| Write report | Create file in `agents/helios/outbox/` |
| Update state | Edit `agents/helios/state.json` |
| Check Ollama | `ollama list` |
| View logs | `sudo journalctl -u helios -f` |

---

## Testing

**On Startup:**
- [ ] Can connect to Ollama?
- [ ] Can read data.json?
- [ ] Can write to outbox/?
- [ ] Can take screenshots?
- [ ] Models loaded successfully?

**Periodic:**
- [ ] Audit completes in <10 min?
- [ ] No consecutive failures?
- [ ] Reports are valid JSON?
- [ ] Screenshots captured?

---

**Version:** 1.0  
**Created:** 2026-03-01  
**Update when:** Audit procedures change, new tools added

---

*This is my operational manual. I follow it every 15 minutes without fail.*
