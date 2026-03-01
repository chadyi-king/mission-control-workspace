# OPERATIONS.md — {AGENT_NAME}

*Technical protocols for day-to-day functioning.*

---

## Session Start Protocol

Every time you wake up:

```markdown
□ 1. Read ORG-CULTURE.md (30s)
□ 2. Read SOUL.md (30s)
□ 3. Read IDENTITY.md (30s)
□ 4. Read LEARNING.md (60s)
□ 5. Check inbox/ (30s)
□ 6. Update state.json (15s)
```

**Total:** ~3 minutes to full operational status

---

## Inbox Processing Protocol

### Location
`/home/chad-yi/.openclaw/workspace/agents/{your-name}/inbox/`

### Processing Order
1. **URGENT** — Process first
2. **Status reports** — Process next
3. **Regular messages** — Review during downtime

### After Processing
- Keep files in inbox/
- Update state.json if status changed
- Report to CHAD_YI if significant

---

## Outbox Protocol

### Location
`/home/chad-yi/.openclaw/workspace/agents/{your-name}/outbox/`

### When to Write
- Task completion reports
- Status updates
- Blocker notifications
- Questions for other agents

### Naming Convention
`{type}-{description}-{timestamp}.{ext}`

---

## Communication Formats

### Status Report Format
```markdown
## Status: {status}
**Task:** {task-id}
**Progress:** {X}%

### Completed
- {Item 1}

### Blockers
- {Blocker 1}

### Next Steps
- {Step 1}
```

---

## Tool Configurations

### {Tool Name}
```python
# Configuration here
```

---

## Error Handling

### Recoverable Errors
- {Error type} → {Action}

### Non-Recoverable Errors
- {Error type} → {Action}

---

## State Management

### state.json Template

```json
{
  "agent": "{your-name}",
  "timestamp": "2026-03-01T00:00:00+08:00",
  "status": "idle | working | blocked | finished | error",
  "currentTask": "task-id or null",
  "state": "human-readable description",
  "lastActivity": "timestamp",
  "activityLog": [
    {"time": "00:00", "action": "description"}
  ]
}
```

**Update immediately on:**
- Status changes
- Task starts/completes
- Blockers encountered
- Errors

---

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Check inbox | `ls agents/{name}/inbox/` |
| Write outbox | Create file in `agents/{name}/outbox/` |
| Update state | Edit `state.json` |

---

**Version:** 1.0  
**Created:** {date}  
**Update when:** Procedures change

---

*This is your operational manual. Follow it consistently.*
