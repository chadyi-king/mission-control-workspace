# HELIOS AUDIT CHECKLIST
## Run this every 15 minutes

## 1. DASHBOARD DATA VERIFICATION

### File: /mission-control-dashboard/data.json
- [ ] File exists and is valid JSON
- [ ] lastUpdated timestamp is within 24 hours
- [ ] stats.totalTasks matches actual count in tasks object
- [ ] stats.tasksDone matches workflow.done.length
- [ ] All workflow arrays contain valid task IDs (exist in tasks object)
- [ ] No duplicate task IDs across arrays
- [ ] All tasks have required fields: id, title, project, status, priority
- [ ] All task status values are valid: pending, active, review, done

### Data Integrity Checks
- [ ] No orphaned task references (task ID in workflow but not in tasks object)
- [ ] No duplicate tasks (same ID appearing multiple times)
- [ ] All projects referenced in tasks exist in projectDetails
- [ ] All task deadlines are valid ISO dates (if present)
- [ ] Completed tasks have completedAt timestamp

## 2. AGENT STATUS VERIFICATION

### Check each agent's files:
| Agent | Files to Check | What to Verify |
|-------|----------------|----------------|
| CHAD_YI | AGENT_STATE.json | Status matches actual activity |
| Helios | AGENT_STATE.json | lastAudit within 15 min |
| Escritor | current-task.md, heartbeat.json | Task matches data.json, not idle >24h |
| Quanta | heartbeat.json, TRADING_SETUP.md | BLOCKED status if no credentials |
| MensaMusa | heartbeat.json | BLOCKED status if no credentials |
| Autour | heartbeat.json | Idle until script tasks assigned |

### Agent Status Rules:
- [ ] If agent has no activity >24h → Mark as idle
- [ ] If agent has current-task.md with work → Mark as active
- [ ] If agent blocked on external dependency → Mark as blocked
- [ ] If agent waiting for user input → Mark as waiting_for_input

## 3. DEADLINE VERIFICATION

### Urgent (Action Required <24h)
- [ ] List all tasks with deadline within 24 hours
- [ ] Verify these are in workflow.pending or workflow.active
- [ ] Flag any overdue tasks (deadline < now)

### Warning (Action Required <48h)
- [ ] List all tasks with deadline 24-48 hours
- [ ] Ensure these are visible in dashboard

### Calendar Accuracy
- [ ] Tasks only appear on their actual deadline date
- [ ] No tasks showing on wrong dates

## 4. CRITICAL ISSUES TO FLAG

### Flag immediately if found:
- [ ] Data.json cannot be parsed (corrupted)
- [ ] Task count mismatch >5 tasks (potential data loss)
- [ ] Agent claiming work they didn't do (authorship mismatch)
- [ ] Security: Unauthorized changes to agent files
- [ ] Overdue deadlines >48h with no action

## 5. AUDIT REPORT FORMAT

```json
{
  "auditId": "audit-2026-02-11T14-15-00",
  "timestamp": "2026-02-11T14:15:00Z",
  "auditor": "Helios",
  "checks": {
    "dataJson": {
      "exists": true,
      "valid": true,
      "lastUpdated": "2026-02-11T14:00:00Z",
      "taskCount": 65,
      "issues": []
    },
    "agents": {
      "checked": ["CHAD_YI", "Helios", "Escritor", "Quanta", "MensaMusa", "Autour"],
      "active": 2,
      "idle": 2,
      "blocked": 2,
      "issues": []
    },
    "deadlines": {
      "urgent": ["A1-1"],
      "warning": ["B6-1", "B6-3"],
      "issues": []
    }
  },
  "findings": [],
  "recommendations": [],
  "escalationRequired": false
}
```

## 6. COMMUNICATION

### After each audit:
1. Write report to: `/agents/helios/outbox/audit-[timestamp].json`
2. If critical issues: Write to `/agents/message-bus/broadcast/urgent-[timestamp].md`
3. Update: `/agents/helios/AGENT_STATE.json` with lastAudit timestamp

### NEVER:
- Modify data.json
- Change dashboard files
- Mark tasks complete without CHAD_YI approval
- Spawn or terminate agents
- Delete any files

### ALWAYS:
- Report findings to CHAD_YI
- Wait for CHAD_YI to make changes
- Document everything in audit reports
- Flag inconsistencies immediately
