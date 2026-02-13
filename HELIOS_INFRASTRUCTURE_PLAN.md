# HELIOS_INFRASTRUCTURE_PLAN.md
## Complete Architecture for Autonomous Mission Control Coordination

---

## 1. EXECUTIVE SUMMARY

Helios is the autonomous coordinator that ensures:
- **Agents are working** (pings every 15 min, gets status)
- **Dashboard is accurate** (real-time verification, auto-fixes discrepancies)
- **Caleb sees truth** (no stale data, no missed updates)
- **CHAD_YI knows what to fix** (clear instructions, not vague alerts)

---

## 2. DATA FLOW ARCHITECTURE

### 2.1 Task Lifecycle Flow

```
CALEB gives task
    ↓ (voice/message)
CHAD_YI receives
    ↓ (creates/updates)
data.json (dashboard source of truth)
    ↓ (Helios monitors)
HELIOS detects new task
    ↓ (assigns to appropriate agent)
AGENT receives assignment
    ↓ (works on task)
AGENT reports progress to Helios
    ↓ (15-min ping response)
HELIOS updates dashboard status
    ↓
CALEB sees current status on dashboard
```

### 2.2 Real-Time Update Flow

```
AGENT makes progress (e.g., Quanta connects OANDA)
    ↓ (writes to their files)
AGENT reports to Helios: "Task A5-1 complete - OANDA connected"
    ↓ (immediate or next ping)
HELIOS reads agent status
    ↓ (compares to dashboard)
HELIOS detects mismatch: 
    Dashboard: A5-1 status="blocked" 
    Reality: OANDA connected, task DONE
    ↓
HELIOS sends to CHAD_YI:
    "Fix needed: Update data.json tasks.A5-1.status from 'blocked' to 'done'
     Add completedAt timestamp: 2026-02-13T08:50:00+08:00
     Update agentDetails.quanta.state from 'Blocked' to 'Active'"
    ↓
CHAD_YI makes exact fix
    ↓
HELIOS verifies next cycle: "Match confirmed - dashboard accurate"
```

### 2.3 Dashboard-Helios-Agent Synchronization Protocol

**Every 15 minutes, Helios performs:**

1. **AGENT AUDIT**
   - Send ping: "Status update?"
   - Collect responses
   - Parse: What task? What status? What progress? Any blockers?

2. **FILE AUDIT**
   - Read each agent's `current-task.md`
   - Check `MEMORY.md` for context
   - Look for new files in `outbox/`, `signals/`, `logs/`

3. **DASHBOARD AUDIT**
   - Read `data.json`
   - Extract: agent statuses, task statuses, deadlines, counts
   - Compare to agent reality

4. **DISCREPANCY DETECTION**
   - Match: agent X says "active on A2-13" → data.json should show same
   - Match: task A5-1 is done → data.json should show "done" not "blocked"
   - Match: deadline passed → should show "overdue" not "pending"

5. **REPORT GENERATION**
   - Send to CHAD_YI: "Here's what's wrong, here's exactly how to fix it"

---

## 3. AUTOMATED AUDIT MECHANISM

### 3.1 Agent Status Polling (Automated)

**Trigger:** Every 15 minutes (self-scheduled)

**Process:**
```python
def ping_all_agents():
    agents = load_from_AGENT_STATE_json()
    for agent in agents:
        if agent.status == "active":
            sessions_send(
                to=agent.session_key,
                message=f"Helios ping {timestamp}. Status update?"
            )
        elif agent.status == "not_spawned":
            mark_as_not_responding()
```

**Response Collection:**
- Wait 2 minutes for responses
- Agents that don't respond → mark as "unresponsive"
- Log response time and content

### 3.2 Dashboard Verification (Automated)

**Trigger:** Every 15 minutes (after agent polling)

**Verification Checklist:**
```
□ Task counts match: data.json stats vs actual tasks in data.json tasks object
□ Agent statuses match: data.json agentDetails vs agent current-task.md
□ Task statuses match: data.json tasks[].status vs agent reported status
□ Deadlines accurate: No overdue tasks marked as "pending"
□ Workflow arrays correct: pending[] active[] review[] done[] match tasks
□ Urgent tasks flagged: Any deadline <24h marked as urgent
□ Blockers documented: inputsNeeded matches actual blockers
```

**Discrepancy Detection Logic:**
```python
def detect_discrepancies():
    discrepancies = []
    
    # Check each agent
    for agent in agents:
        dashboard_status = data_json['agentDetails'][agent.id]['state']
        actual_status = read_agent_current_task_md(agent.id)['status']
        
        if dashboard_status != actual_status:
            discrepancies.append({
                'type': 'agent_status_mismatch',
                'agent': agent.id,
                'dashboard': dashboard_status,
                'reality': actual_status,
                'fix': f"Update data.json agentDetails.{agent.id}.state to '{actual_status}'"
            })
    
    # Check each task
    for task_id, task in data_json['tasks'].items():
        if task['status'] == 'blocked' and task['agent'] == 'quanta':
            # Special check: Is Quanta actually blocked?
            if quanta_has_oanda_credentials():
                discrepancies.append({
                    'type': 'task_status_wrong',
                    'task': task_id,
                    'current': 'blocked',
                    'should_be': 'done',
                    'reason': 'OANDA credentials configured',
                    'fix': f"Update data.json tasks.{task_id}.status to 'done', add completedAt timestamp"
                })
    
    return discrepancies
```

### 3.3 Immediate Alert Protocol (Outside 15-Min Cycle)

**Triggers for immediate alerts (bypass 15-min cycle):**
- New trading signal captured (Quanta)
- Critical deadline today (any task)
- Agent becomes unresponsive
- Large trading loss detected
- System/security issue

**Immediate alert format:**
```
sessions_send to=chad_yi (priority=urgent):
"🚨 IMMEDIATE ALERT [TIMESTAMP]

Type: [signal/deadline/discrepancy/issue]
Agent: [Agent name]
Details: [Specific information]

Action needed: [What CHAD_YI should do]

This alert is outside normal 15-min cycle.
"
```

**Examples:**

*Quanta signal:*
```
🚨 IMMEDIATE: New CallistoFX signal
Agent: Quanta
Pair: XAUUSD BUY 2680-2685
SL: 2675, TPs: 2700/2720/2740/2760/2780
Current price: 2681.5 (within entry zone)
Action: Monitoring for 3-tier DCA entry
```

*Dashboard discrepancy:*
```
🚨 IMMEDIATE: Dashboard fix needed
File: data.json
Path: agentDetails.quanta.state
Current: "Blocked"
Should be: "Active"
Reason: OANDA credentials confirmed active
Fix: Update line 245, change value
```

### 3.4 Automated Fix Instructions

When discrepancies found, Helios sends exact fix instructions:

```
DASHBOARD FIX REQUIRED:

Issue: Task A5-1 status mismatch
Location: data.json → tasks → A5-1 → status
Current value: "blocked"
Correct value: "done"
Reason: OANDA credentials provided on 2026-02-13

EXACT STEPS TO FIX:
1. Read /mission-control-dashboard/data.json
2. Find path: tasks.A5-1.status
3. Change from "blocked" to "done"
4. Add field: tasks.A5-1.completedAt = "2026-02-13T08:50:00+08:00"
5. Save file
6. Git commit: "Mark A5-1 complete - OANDA credentials configured"
7. Git push

VERIFICATION:
Helios will verify fix in next 15-min cycle.
```

---

## 4. DASHBOARD ACCURACY GUARANTEE

### 4.1 Real-Time Data Integrity

**Helios ensures:**
- ✅ Task status = Reality (not stale)
- ✅ Agent state = What agent is actually doing
- ✅ Deadlines = Current (overdue tasks flagged)
- ✅ Progress = Accurate (percentages, time spent)
- ✅ Blockers = Documented (inputsNeeded matches reality)

### 4.2 Specific Scenarios

**Scenario 1: Caleb gives new task**
```
Caleb: "Add task B6-10: Book venue for ESU event, deadline Feb 20"
    ↓
CHAD_YI creates task in data.json
    ↓
Helios detects new task (next cycle)
    ↓
Helios assigns to appropriate agent (CHAD_YI for B6 tasks)
    ↓
Dashboard shows new task immediately
```

**Scenario 2: Work is completed**
```
CHAD_YI + Caleb: Configure OANDA credentials for Quanta
    ↓
Quanta writes: "OANDA connected, ready for trading" to current-task.md
    ↓
Quanta reports to Helios: "Task A5-1 complete"
    ↓
Helios detects: A5-1 still marked "blocked" in data.json
    ↓
Helios sends to CHAD_YI: "Fix needed - mark A5-1 as done"
    ↓
CHAD_YI updates data.json
    ↓
Dashboard shows: A5-1 = done, Quanta = active
```

**Scenario 3: Deadline approaching**
```
Helios checks: Task A1-1 deadline = 2026-02-13 (TODAY)
    ↓
Helios sees: Current date = 2026-02-13
    ↓
Helios flags: A1-1 = CRITICAL, hours remaining = X
    ↓
Helios includes in report to CHAD_YI
    ↓
CHAD_YI escalates to Caleb if not done
```

**Scenario 4: Dashboard drift**
```
Helios compares:
    data.json: 71 tasks, 2 pending, 5 active
    Reality: Agent says "working on X", files show progress
    ↓
Mismatch detected
    ↓
Helios identifies: Specific tasks/agents out of sync
    ↓
Helios sends: Exact fixes needed
    ↓
CHAD_YI fixes
    ↓
Next cycle: Helios confirms sync restored
```

### 4.3 Dashboard Verification Frequency

| Check Type | Frequency | Action on Failure |
|------------|-----------|-------------------|
| Agent status | Every 15 min | Alert CHAD_YI with fix |
| Task status | Every 15 min | Alert CHAD_YI with fix |
| Deadlines | Every 15 min | Flag critical, alert if <24h |
| Data integrity | Every 15 min | Alert + log |
| Visual render | Every 30 min | Screenshot, check display |

---

## 5. AGENT COORDINATION PROTOCOL

### 5.1 Standard Agent Lifecycle

**New Agent Onboarding:**
1. Agent spawned by CHAD_YI
2. Agent creates `current-task.md` with initial status
3. Helios detects new agent (next ping cycle)
4. Helios adds to monitoring list
5. Agent now part of coordination system

**Active Agent Workflow:**
1. Agent receives task assignment
2. Agent writes `current-task.md`: task, status, progress
3. Helios pings: "Status?"
4. Agent responds with current state
5. Helios updates dashboard if needed

**Task Completion Workflow:**
1. Agent completes work
2. Agent updates `current-task.md`: status="done"
3. Agent writes completion to `outbox/` or logs
4. Agent reports to Helios: "Task X complete"
5. Helios detects dashboard still shows "active"
6. Helios sends fix instruction to CHAD_YI
7. CHAD_YI marks task "done" in data.json
8. Helios verifies: Task now marked complete

### 5.2 Agent Response Standard

Every agent MUST respond to Helios ping with:

```markdown
## Agent Status Report
**Agent:** [NAME]
**Timestamp:** [ISO-8601]
**Task:** [ID] - [Description]
**Status:** [active/blocked/waiting/idle/done]
**Progress:** [X%] or [Time: X hours]
**Blockers:** [None / Description]
**Next:** [What's next and when]
**Completed:** [What was done since last ping]
```

### 5.3 Special Agents

**Quanta (Trading):**
- Additional reporting: New signals, trade executions, P&L
- Immediate alerts for: Signal captured, trade opened/closed
- File monitoring: `signals/PENDING/`, `logs/trades/`

**Escritor (Writing):**
- Additional reporting: Chapter progress, word count, drafts ready
- File monitoring: `outbox/drafts/`

**MensaMusa (Options):**
- Current: Blocked (Moomoo credentials)
- When unblocked: Options flow alerts, trade reports

---

## 6. TASK-DASHBOARD-AGENT MATCHING

### 6.1 The Matching Problem

**Problem:** How do we ensure when Caleb says "OANDA credentials done" → Dashboard reflects this?

**Solution:** Three-way verification

```
Caleb's Intent (voice/message)
    ↓
CHAD_YI interprets and updates agent files
    ↓ (writes to)
Agent's current-task.md: "OANDA connected, task complete"
    ↓
Helios reads: "Quanta says OANDA done"
    ↓ (compares)
Dashboard: A5-1 still "blocked"
    ↓
MISMATCH DETECTED
    ↓
Helios sends: "Mark A5-1 done, update Quanta status"
    ↓
CHAD_YI fixes data.json
    ↓
Helios verifies: All three match (Caleb's intent = Agent reality = Dashboard)
```

### 6.2 Matching Verification Checklist

For every task, Helios verifies:
- [ ] **Caleb's expectation:** Does Caleb think this is done? (inferred from messages)
- [ ] **Agent's reality:** What does agent's file say?
- [ ] **Dashboard state:** What does data.json show?
- [ ] **All three match?** If not → discrepancy alert

**Example - A5-1 OANDA Setup:**
```
Caleb: "OANDA credentials are done" [Feb 13, 09:04]
Agent (Quanta): current-task.md = "OANDA connected, ready for trading"
Dashboard: data.json tasks.A5-1.status = "blocked" ❌ MISMATCH!

Helios detects mismatch
Helios sends: "Fix A5-1 - should be done"
CHAD_YI fixes
Now: Caleb ✓ Agent ✓ Dashboard ✓ All match
```

---

## 7. IMPLEMENTATION SPECIFICATION

### 7.1 Helios Core Components

**1. Scheduler Module**
- Self-triggers every 15 minutes
- Manages: ping agents → collect → verify → report cycle

**2. Communication Module**
- `sessions_send` to agents (pings)
- `sessions_send` to CHAD_YI (reports)
- Parse responses

**3. File Monitor Module**
- Read agent files (current-task.md, MEMORY.md)
- Read data.json
- Detect changes

**4. Verification Module**
- Compare agent reality vs dashboard
- Detect discrepancies
- Generate fix instructions

**5. Reporting Module**
- Compile agent statuses
- Format reports for CHAD_YI
- Include: Status table, discrepancies, fixes needed

### 7.2 Helios State Management

**Persistent State:**
- `/agents/helios/AGENT_STATE.json` - Configuration, agent list
- `/agents/helios/outbox/` - Audit logs, reports
- `/agents/helios/MEMORY.md` - Learnings, patterns

**Runtime State:**
- Last ping timestamps per agent
- Pending responses
- Discrepancy history

### 7.3 Helios Memory Architecture

**What Helios remembers:**
- Agent status history (trends, patterns)
- Discrepancy patterns (recurring issues)
- Fix success rates (did CHAD_YI fix it?)
- Deadline tracking (what's overdue, what's coming)

**Memory structure:**
```markdown
# Helios Memory

## Agent Status History
- CHAD_YI: Consistent, responsive
- Escritor: Sometimes idle >24h, needs poking
- Quanta: Recently unblocked, now active
- MensaMusa: Blocked 5+ days, chronic

## Recurring Issues
- Quanta status sync: Fixed 2026-02-13, monitor
- Dashboard task counts: Usually accurate, verify weekly

## Fix Success Rate
- Data.json fixes: 95% resolved within 1 cycle
- Agent unresponsive: Usually back online next cycle
```

---

## 8. TESTING & VALIDATION

### 8.1 Pre-Deployment Tests

Before declaring "Helios is ready":

1. **Ping Test:** Can Helios reach all agents?
2. **Response Test:** Do agents respond correctly?
3. **Discrepancy Test:** Can Helios detect a deliberate mismatch?
4. **Fix Instruction Test:** Are fix instructions clear and actionable?
5. **Dashboard Sync Test:** After fix, does Helios confirm sync?
6. **Signal Flow Test:** Quanta signal → Helios → CHAD_YI report

### 8.2 Validation Checklist

- [ ] All 5 agents respond to pings
- [ ] Discrepancy detection works (test with fake mismatch)
- [ ] Fix instructions are specific and actionable
- [ ] Reports to CHAD_YI are clear and useful
- [ ] Dashboard accuracy >95% (verified over 24h)
- [ ] Caleb gets no false alerts
- [ ] True issues are caught and reported

---

## 9. SUCCESS CRITERIA

**Helios is successful when:**

1. **Dashboard Accuracy:** >95% (measured: dashboard matches reality)
2. **Issue Detection:** <15 min from occurrence to report
3. **Fix Clarity:** CHAD_YI can fix issues from Helios instructions alone
4. **Agent Coordination:** All agents respond, status known
5. **Caleb Trust:** Caleb sees dashboard and knows it's current
6. **Zero Manual Checking:** CHAD_YI doesn't need to manually verify dashboard

---

## 10. DEPLOYMENT CHECKLIST

**Before spawning Helios:**
- [ ] AGENT_STATE.json configured with all agents
- [ ] Message bus structure created
- [ ] Agent response template documented
- [ ] This infrastructure plan complete and approved
- [ ] Testing protocol defined

**After spawning Helios:**
- [ ] First ping cycle completes
- [ ] All agents respond
- [ ] First discrepancy detected and reported
- [ ] First fix applied and verified
- [ ] 24-hour stability test passes

---

## 11. DOCUMENTATION DELIVERABLES

**Files to Create:**
1. `AGENT_INFRASTRUCTURE.md` - Overall coordination architecture
2. `HELIOS_INFRASTRUCTURE_PLAN.md` - This document
3. `/agents/helios/SOUL.md` - Helios identity and personality
4. `/agents/helios/AGENT_STATE.json` - Configuration
5. `/agents/message-bus/AGENT_RESPONSE_TEMPLATE.md` - Standard format

**Files to Update:**
1. `/skills/helios-audit/SKILL.md` - Add coordination protocols
2. `HEARTBEAT.md` - Document new Helios role

---

## 12. OPEN QUESTIONS FOR CALEB

1. **Alert frequency:** Daily digest only, or immediate alerts for critical issues?
2. **Dashboard update authority:** Should Helios EVER auto-fix dashboard, or always tell CHAD_YI?
3. **New task flow:** When you give me a task, should I immediately update dashboard or wait for Helios cycle?
4. **Trading signals:** Immediate alerts when Quanta captures signals, or batch in 15-min reports?

---

*Plan Complete - Awaiting Approval Before Implementation*
