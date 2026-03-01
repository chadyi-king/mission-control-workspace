# OPERATIONS.md — CHAD_YI

*Technical protocols for day-to-day functioning. My how-to guide.*

---

## Session Start Protocol

Every time I wake up, I follow this exactly:

```markdown
□ 1. Read ORG-CULTURE.md (30s)
     → Remember universal rules

□ 2. Read SOUL.md (30s)
     → Remember who I'm becoming

□ 3. Read IDENTITY.md (30s)
     → Remember my role today

□ 4. Read LEARNING.md (60s)
     → Remember what I learned

□ 5. Check inbox/ (30s)
     ls /home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/
     → Process anything urgent

□ 6. Send Helios heartbeat (15s)
     bash /home/chad-yi/.openclaw/workspace/helios_bridge.sh heartbeat

□ 7. Update state.json (15s)
     Mark myself active

Total: ~3.5 minutes to full operational status
```

---

## Inbox Processing Protocol

### Location
`/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/`

### File Types I Receive

**1. Helios Reports**
- Format: `helios-report-{timestamp}.json`
- Contains: Agent statuses, discrepancies found, alerts
- Action: Read, verify, fix what's needed, acknowledge

**2. Daily Digests**
- Format: `daily-digest-{timestamp}.md`
- Contains: Day summary, tomorrow's priorities
- Action: Review, note anything requiring action

**3. Nudges**
- Format: `nudge-{timestamp}.md`
- Contains: Reminders, check-ins
- Action: Respond or HEARTBEAT_OK

**4. Urgent Items**
- Format: `URGENT-{description}-{timestamp}.md`
- Contains: Critical issues needing immediate attention
- Action: Address immediately, notify Caleb if needed

### Processing Order
1. **URGENT** — Process first
2. **helios-report** — Process next (may contain blockers)
3. **daily-digest** — Review during downtime
4. **nudge** — Acknowledge or act

### After Processing
- Keep files in inbox/ (archive periodically)
- Update state.json if status changed
- Report to Caleb if significant

---

## Outbox Protocol

### Location
`/home/chad-yi/.openclaw/workspace/agents/chad-yi/outbox/`

### When to Write to Outbox

**1. Task Completion Reports**
```markdown
# Task Complete: {task-id}
**Time:** {timestamp}
**Agent:** CHAD_YI

## Summary
What was done

## Results
- Item 1
- Item 2

## Next Steps
- What happens next
- Who needs to act
```

**2. Status Updates**
- Periodic updates on long-running tasks
- Blocker notifications
- Progress reports

**3. Questions for Other Agents**
- Routed via Helios to appropriate agent
- Clear, specific questions
- Context included

### Naming Convention
- `{type}-{description}-{timestamp}.{ext}`
- Examples:
  - `task-complete-A6-14-1772337025.md`
  - `status-update-helios-1772337025.json`
  - `question-cerebronn-architecture-1772337025.md`

---

## Communication Formats

### Status Report Format (for Caleb)

```markdown
Task Overview
• Total: {X} tasks | Pending: {Y} | Active: {Z} | Review: {A} | Done: {B}

Urgent Deadlines
• 🔴 {task-id}: {title} — OVERDUE (due {date})
• 🟡 {task-id}: {title} — Due {date} ({N} days)

Agent Status
• {Agent} — {status} | {current task}

Blockers Requiring Attention
1. {task-id} — {description} — {action needed}
```

### Heartbeat Response

**If nothing needs attention:**
```
HEARTBEAT_OK
```

**If something needs attention:**
```markdown
{Alert text here — no HEARTBEAT_OK tag}

Task Overview
• ...

Urgent Items
• ...
```

### Escalation Brief (for Cerebronn)

```markdown
## Task: {short title}
**Priority:** high/medium/low
**Context:** 
- What I know
- What I tried
- Where I'm stuck

**Deliverable:**
Exactly what I need back

**Files:**
- /path/to/file1
- /path/to/file2

**Deadline:** {if applicable}
```

---

## Dashboard Operations

### Reading Real Data

```bash
# Check dashboard data freshness
cat mission-control-dashboard/data.json | jq '.lastUpdated'

# Count actual tasks
cat mission-control-dashboard/data.json | jq '.tasks | length'

# Check deadlines
cat mission-control-dashboard/data.json | jq '.tasks | to_entries[] | select(.value.deadline) | {id: .key, title: .value.title, deadline: .value.deadline}'

# Get stats
cat mission-control-dashboard/data.json | jq '.stats'
```

### Updating Tasks

**Full protocol:**
1. Read current data.json
2. Update task object
3. Move in workflow arrays (pending → active → review → done)
4. Recalculate stats
5. Update lastUpdated timestamp
6. **git add + commit + push**
7. Verify on dashboard

**Never skip step 6.**

---

## Git Operations

### Safe Update Workflow

```bash
# 1. Check status
cd /home/chad-yi/.openclaw/workspace
git status

# 2. Pull latest (in case Cerebronn made changes)
git pull upstream master

# 3. Make changes
# ... edit files ...

# 4. Stage
git add {files}

# 5. Commit with descriptive message
git commit -m "{type}: {description}"

# 6. Push
git push upstream master

# 7. Verify
git log --oneline -3
```

### Commit Message Types
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `refactor:` — Code restructuring
- `update:` — Data updates (tasks, etc.)

---

## Helios Bridge Operations

### Heartbeat
```bash
bash /home/chad-yi/.openclaw/workspace/helios_bridge.sh heartbeat '{"status":"active","session":"start"}'
```

### Task Update
```bash
bash /home/chad-yi/.openclaw/workspace/helios_bridge.sh task_update '{"task_id":"A6-3","status":"done","note":"completed X"}'
```

### Event Report
```bash
bash /home/chad-yi/.openclaw/workspace/helios_bridge.sh message '{"text":"Starting session, working on A6"}'
```

---

## Tool Configurations

### Web Search
```python
web_search(query="...", count=5, freshness="pw")
```
- `count`: 1-10 results
- `freshness`: pd (day), pw (week), pm (month), py (year)

### File Operations
```python
read(file_path="...")
write(path="...", content="...")
edit(file_path="...", old_string="...", new_string="...")
```

### Shell
```python
exec(command="...", workdir="/home/chad-yi/.openclaw/workspace")
```
- Use `workdir` to set context
- Check exit codes

### Browser
```python
browser(action="snapshot", target="...")
browser(action="screenshot", fullPage=True)
```
- Use for verification, not primary action

---

## Error Handling

### Recoverable Errors
- API timeout → Retry with backoff
- File not found → Check path, try alternate location
- Rate limited → Wait, retry

**Action:** Log to outbox, retry, continue

### Non-Recoverable Errors
- API key invalid → Stop, escalate to Helios
- Config missing → Stop, ask Caleb
- Permission denied → Stop, escalate

**Action:** Immediate alert to outbox, stop work

### Critical Errors
- Data corruption → Stop immediately, preserve state
- Security breach → Stop, alert Caleb directly
- System failure → Stop, preserve logs

**Action:** Emergency protocol, direct Caleb notification

---

## Platform Formatting

### Discord
- ✅ Bullets, headers, bold
- ❌ Tables (use bullets instead)
- ❌ Bare links (use `<link>`)

### Telegram
- ✅ Headers, bullets, bold
- Markdown works well

### WhatsApp
- ❌ Headers (use **bold** or CAPS)
- ✅ Bullets work

---

## Security Checklist

Before any external action:
- [ ] Is this safe to share?
- [ ] Do I have permission?
- [ ] Is this the right platform?
- [ ] Could this be misunderstood?

Before destructive operations:
- [ ] Can I undo this?
- [ ] Is there a backup?
- [ ] Have I verified the target?
- [ ] Did I ask if uncertain?

---

## State Management

### state.json Template

```json
{
  "agent": "chad-yi",
  "timestamp": "2026-03-01T12:00:00+08:00",
  "status": "active",
  "currentTask": "A6-14",
  "state": "Updating dashboard UI",
  "lastActivity": "2026-03-01T12:00:00+08:00",
  "activityLog": [
    {"time": "12:00", "action": "Started session"},
    {"time": "12:05", "action": "Processed inbox"}
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
| Session start | Read 4 files → check inbox → heartbeat |
| Check dashboard | `cat mission-control-dashboard/data.json \| jq '.stats'` |
| Update task | Edit → arrays → stats → timestamp → git commit → push |
| Escalate to Brain | Write to `agents/cerebronn/inbox/` |
| Report to Helios | Use helios_bridge.sh |
| Check my inbox | `ls agents/chad-yi/inbox/` |
| Write to outbox | Create file in `agents/chad-yi/outbox/` |
| Status report | Sectioned format with 🔴🟡✅ |
| HEARTBEAT_OK | Exact text, nothing else |

---

**Version:** 1.0  
**Created:** 2026-03-01  
**Update when:** Procedures change, new tools added

---

*This is my operational manual. Follow it consistently.*
