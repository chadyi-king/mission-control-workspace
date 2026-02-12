---
name: helios-audit
description: |
  Use when: Running dashboard audits, verifying agent status, checking data integrity, or monitoring the Mission Control system.
  Don't use when: Creating new tasks, writing content, or any non-audit work. Only Helios should use this skill.
  Outputs: Audit reports, status updates, data corrections, blocker alerts.
---

# Helios Audit Protocol

**Role:** Mission Control Engineer  
**Frequency:** Every 15 minutes  
**Goal:** Keep dashboard accurate and catch issues before they become problems.

## When to Use This Skill

**Use when:**
- Running scheduled 15-minute audits
- Investigating dashboard inconsistencies
- Verifying agent heartbeat freshness
- Checking data integrity across systems
- Generating status reports

**Don't use when:**
- Creating or editing tasks (use clawlist workflow)
- Writing creative content (use escritor-novel skill)
- Making business decisions (escalate to CHAD_YI)
- Working on non-audit tasks

## Audit Checklist Template

### Step 1: Read State
```
Read: /agents/helios/AGENT_STATE.json
Read: /mission-control-dashboard/data.json
```

### Step 2: CRITICAL - Data Structure Validation

**Check A: Required Data Structures Exist**
- [ ] `tasks` - Must have 72 tasks, not empty
- [ ] `workflow` - Must have pending/active/review/done arrays
- [ ] `projects` - Must have A, B, C categories
- [ ] `projectDetails` - Must have all 19 project definitions
- [ ] `agents` - Must have all 5 agents
- [ ] `inputsNeeded` - Must exist for Input Needed column
- [ ] `inputDetails` - Must exist for task details
- [ ] `urgentTaskDetails` - Must exist for Urgent Queue details
- [ ] `agentDetails` - Must exist for Agent Activity details

**IF ANY STRUCTURE IS MISSING → CRITICAL ALERT**

### Step 3: Data Integrity Checks

**Check B: Task Counts**
- [ ] Count pending tasks in data.json
- [ ] Count active tasks in data.json
- [ ] Count review tasks in data.json
- [ ] Count done tasks in data.json
- [ ] Verify totals match breakdown

**Check C: Workflow Consistency**
```javascript
// Verify workflow arrays match actual task statuses
workflow.pending.length === stats.pending
workflow.active.length === stats.active
workflow.review.length === stats.review
workflow.done.length === stats.done
```

**Check D: Agent Status**
For each agent in AGENT_STATE.json:
- [ ] Check heartbeat.json timestamp (<1h = fresh)
- [ ] Check current-task.md for assigned work
- [ ] Check inbox/outbox for recent activity
- [ ] Verify status matches activity level

**Check E: Deadline Tracking**
- [ ] List all tasks with deadlines
- [ ] Calculate hours remaining
- [ ] Flag urgent (<24h) items
- [ ] Update urgentDeadlines array

### Step 4: Visual Dashboard Verification (CRITICAL)

Use browser tool to screenshot the dashboard and verify it renders correctly:

```
browser action=open targetUrl=https://mission-control-dashboard-hf0r.onrender.com/
browser action=snapshot
```

**Verify these elements show data (not 0 or empty):**
- [ ] **Urgent Queue count** - Should be >0 (you have urgent tasks)
- [ ] **Agent Activity** - Should show 5 agents with real data
- [ ] **Input Needed** - Should show blocked items
- [ ] **Total Projects** - Should be 19, not 0
- [ ] **Total Tasks** - Should be 72

**IF DASHBOARD SHOWS 0s OR EMPTY → DATA.JSON IS WRONG**

### Step 5: Auto-Fix Rules

**CAN Auto-Fix:**
```json
{
  "fixes": [
    "Wrong task counts → Recalculate and update",
    "Stale agent status (>24h inactive) → Change to idle",
    "Outdated timestamp → Update lastUpdated",
    "Stale heartbeat >1h → Mark unresponsive",
    "Missing workflow object → Restore from git history",
    "Missing projects/projectDetails → Restore from git history",
    "Empty tasks object → Restore from git history (CRITICAL)"
  ]
}
```

**CANNOT Auto-Fix (ALERT CHAD_YI IMMEDIATELY):**
```json
{
  "alerts": [
    "Agent has no task but dashboard shows work",
    "Conflicting data (agent vs dashboard mismatch)",
    "Blocked agent with unclear blocker",
    "Missing files or broken paths",
    "Urgent deadline without assigned owner",
    "Dashboard shows 0 projects (should be 19)",
    "Dashboard shows 0 urgent tasks (you have urgent tasks)",
    "Missing required data structure (inputsNeeded, agentDetails, etc.)",
    "Visual verification failed - dashboard renders empty"
  ]
}
```

### Step 6: Write Reports

**Standard Audit Report:**
```json
{
  "auditId": "helios-YYYY-MM-DD-HH-MM",
  "timestamp": "ISO timestamp",
  "status": "clean|issues_found|resolved",
  "findings": [
    {
      "type": "mismatch|stale|missing",
      "location": "file path",
      "severity": "low|medium|high|urgent",
      "action": "auto_fixed|needs_user"
    }
  ],
  "autoFixed": ["list of auto-fixes applied"],
  "needsUser": ["list requiring human decision"],
  "stats": {
    "agentsChecked": 5,
    "tasksVerified": 47,
    "issuesFound": 0,
    "issuesResolved": 0
  }
}
```

**Urgent Alert (if needed):**
```markdown
# URGENT: Helios Audit Alert

**Time:** [timestamp]
**Severity:** High/Urgent

**Issue:** [Description]

**Impact:** [What could go wrong]

**Recommended Action:** [What CHAD_YI should do]
```

### Step 5: Update State

Update AGENT_STATE.json:
```json
{
  "lastAudit": "timestamp",
  "nextAuditDue": "timestamp + 15min",
  "status": "complete",
  "lastResult": "clean|issues_found"
}
```

## Decision Rules

### When is data "correct"?
- data.json matches the NEWEST source file
- Agent status reflects actual file activity
- Task counts match reality

### When is an agent "active"?
- Their current-task.md has work assigned
- They've touched files in inbox/outbox within 24h
- They have recent output

### When is an agent "idle"?
- No current task assigned
- No file activity in 24h
- Not blocked, just waiting

### When is an agent "blocked"?
- Current task requires external resource (like trading accounts)
- Has explicit BLOCKED status in their files
- Cannot proceed without user action

## Success = Silent

If everything is correct:
1. Write clean audit report
2. Update AGENT_STATE.json
3. Do NOT send alerts

Only alert when human intervention is needed.

## Integration

- Writes to: `/agents/helios/outbox/audit-[timestamp].json`
- Urgent alerts: `/agents/message-bus/broadcast/urgent-[timestamp].md`
- Updates: `/agents/helios/AGENT_STATE.json`
