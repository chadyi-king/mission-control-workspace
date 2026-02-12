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

### Step 2: Data Integrity Checks

**Check A: Task Counts**
- [ ] Count pending tasks in data.json
- [ ] Count active tasks in data.json
- [ ] Count review tasks in data.json
- [ ] Count done tasks in data.json
- [ ] Verify totals match breakdown

**Check B: Agent Status**
For each agent in AGENT_STATE.json:
- [ ] Check heartbeat.json timestamp (<1h = fresh)
- [ ] Check current-task.md for assigned work
- [ ] Check inbox/outbox for recent activity
- [ ] Verify status matches activity level

**Check C: Deadline Tracking**
- [ ] List all tasks with deadlines
- [ ] Calculate hours remaining
- [ ] Flag urgent (<24h) items
- [ ] Update urgentDeadlines array

### Step 3: Auto-Fix Rules

**CAN Auto-Fix:**
```json
{
  "fixes": [
    "Wrong task counts → Recalculate and update",
    "Stale agent status (>24h inactive) → Change to idle",
    "Outdated timestamp → Update lastUpdated",
    "Stale heartbeat >1h → Mark unresponsive"
  ]
}
```

**CANNOT Auto-Fix (Alert CHAD_YI):**
```json
{
  "alerts": [
    "Agent has no task but dashboard shows work",
    "Conflicting data (agent vs dashboard mismatch)",
    "Blocked agent with unclear blocker",
    "Missing files or broken paths",
    "Urgent deadline without assigned owner"
  ]
}
```

### Step 4: Write Reports

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
