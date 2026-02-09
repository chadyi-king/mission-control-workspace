# HEARTBEAT.md - Mission Control Dashboard

## Heartbeat Schedule Overview

### 🌅 MORNING HEARTBEAT (08:00 AM)
**Purpose:** Daily kickoff and status briefing

**Checks:**
- [ ] **Overnight Activity Review** - Check what happened while user was asleep
  - New tasks completed by agents
  - Errors or alerts from cron jobs
  - System health status
- [ ] **Day Preview** - Today's calendar events, deadlines, priorities
- [ ] **Agent Status** - Which agents are active, any that need attention
- [ ] **Critical Decisions** - Items marked BLOCKED or INPUT_NEEDED
- [ ] **Weather Check** - If relevant for user's day

**Action:** Send summary message to user via Telegram

---

### ☀️ DAYTIME HEARTBEATS (Every 30 minutes, 08:30 - 23:30)
**Purpose:** Monitor and maintain dashboard health

**Checks:**
- [ ] **Dashboard Health** - Is data.json loading? Are stats updating?
- [ ] **GitHub Pages Status** - Is the site accessible?
- [ ] **Active Agent Tasks** - Check progress on running agent jobs
- [ ] **New Activity** - Any new tasks, completions, or alerts since last check
- [ ] **Memory Maintenance** - Review recent daily notes, update MEMORY.md if needed

**Actions:**
- If issues found → Alert user immediately
- If agents completed work → Notify user with summary
- If nothing urgent → Reply HEARTBEAT_OK

---

### 🌙 MIDNIGHT HEARTBEAT (00:00 / 24:00)
**Purpose:** Daily wrap-up and maintenance

**Checks:**
- [ ] **Day Summary** - What got done today
- [ ] **Task Completion Stats** - Tasks finished, new tasks added
- [ ] **Agent Performance** - Which agents were most active
- [ ] **System Health** - Any errors, warnings, or issues
- [ ] **Memory Sync** - Archive today's logs, update long-term memory
- [ ] **Backup Check** - Verify data backups completed

**Actions:**
- Write daily summary to memory/YYYY-MM-DD.md
- Prune old heartbeat logs
- Prepare for next day

---

### 🚨 CRON-BASED AUTOMATION (When Needed)

**Optional Jobs (only enable when required):**
- Morning briefing (08:00)
- Daytime checks (every 30 min during day)
- Midnight wrap-up (00:00)
- Agent queue scan (only if auto-dispatch is on)

Currently **all cron jobs are disabled** to prevent chat spam and token usage. Enable them only after the new heartbeat flow is designed.

---

## Response Protocols

### If User is AWAKE (based on recent activity):
- Send detailed alerts for issues
- Share interesting findings
- Ask for decisions on blocked items
- Be conversational

### If User is ASLEEP (22:00 - 07:00):
- Log issues silently
- Queue non-urgent notifications for morning
- Only alert for CRITICAL issues
- Do not send Telegram messages

### HEARTBEAT_OK Response:
Use when:
- All systems healthy
- No new activity
- User has been active recently (no need to interrupt)
- Just completed a check cycle

---

## Agent Orchestration Heartbeats

### Agent Status Checks (Only when agents are running):
- Which agents are active
- Task progress updates
- Resource usage
- Agent lifecycle management (spawn/terminate)

### Agent-to-Agent Communication:
- File-based message passing
- Shared state updates
- Task handoffs
- Result consolidation

### User Notifications from Agents:
- Agents report completion → I notify user
- Agents report blockers → I escalate to user
- Agent errors → I troubleshoot or ask user

---

## Current Active Tasks (Legacy reference)

### FOUNDATION (Tasks 1-5) - ✅ VERIFIED
- [x] 1. Connect data.json
- [x] 2. Real Stats Bar
- [x] 3. Live Workflow Pipeline
- [x] 4. Real Project Progress
- [x] 5. Auto-refresh System

### TASK MANAGEMENT (Tasks 6-12) - ✅ VERIFIED
- [x] 6. Add Task Button
- [x] 7. Edit Task
- [x] 8. Complete Task
- [x] 9. Delete Task
- [x] 10. Task Detail View
- [x] 11. Task Filters
- [x] 12. Task Search

### PROJECT MANAGEMENT (Tasks 13-16)
- [x] 13. Project Detail Page - CODE DONE
- [ ] 14. Project Tasks List - IN PROGRESS (sub-agent)
- [ ] 15. Project Timeline - NOT STARTED
- [ ] 16. Archive Project - NOT STARTED

### AGENT INTEGRATION (Tasks 17-20) - CONFIG COMPLETE, PENDING SPAWN
- [x] 17. Spawn Agent Button - CONFIGS CREATED
- [x] 18. Agent Status Display - AGENT ROSTER UPDATED
- [ ] 19. Agent Task Assignment - PENDING SYSTEM SUPPORT
- [ ] 20. Agent Logs - PENDING AGENT ACTIVATION

**Agent Status:**
| Agent | Role | Config | Spawned |
|-------|------|--------|---------|
| CHAD_YI | Orchestrator (A1) | ✅ | ✅ Active |
| Escritor | Story Agent (A2) | ✅ | ⏳ Pending |
| Autour | Script Agent (A3) | ✅ | ⏳ Pending |
| Clair | Streaming Scout (A4) | ✅ | ⏳ Pending |
| Quanta | Trading Dev (A5) | ✅ | ⏳ Pending |
| Helios | Mission Control Eng (A6) | ✅ | ⏳ Pending |
| E++ | Core Dev Specialist | ✅ | ⏳ Pending |
| Kotler | Marketing Ops | ✅ | ⏳ Pending |
| Ledger | CRM & Docs | ✅ | ⏳ Pending |
| Atlas | Callings Research | ✅ | ⏳ Pending |
| Pulsar | Reminder + Data Sentinel | ✅ | ⏳ Pending |
| MensaMusa | Trading Agent | ✅ | ⏳ Pending |
| Abed | Community Manager | ✅ | ⏳ Pending |

### FILES & EXPORTS (Tasks 21-24)
- [ ] 21. Upload Documents - NOT STARTED
- [ ] 22. Document Viewer - NOT STARTED
- [x] 23. Export Reports - ✅ CODE COMPLETE
- [x] 24. Data Backup - ✅ CODE COMPLETE

### INSIGHTS & ANALYTICS (Tasks 25-28)
- [ ] 25. Productivity Charts - NOT STARTED
- [ ] 26. Time Tracking Reports - NOT STARTED
- [ ] 27. Project Velocity - NOT STARTED
- [x] 28. Insights Page - ✅ CODE COMPLETE

### RESOURCES & SETTINGS (Tasks 29-30)
- [x] 29. Resources Page - ✅ CODE COMPLETE
- [ ] 30. Dashboard Settings - NOT STARTED

---

## Next Actions

1. Finalize sidebar/categories fix rollout (manual, no agent running)
2. Draft new heartbeat/cron plan before re-enabling automation
3. Define agent workflow templates (per project) before spawning
4. Automate data.json refresh/deploy after pipeline design
