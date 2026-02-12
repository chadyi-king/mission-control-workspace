# HEARTBEAT.md - Mission Control Dashboard

## Dashboard URLs
- **Primary (Render):** https://mission-control-dashboard-hf0r.onrender.com/ ← **USE THIS**
- **Legacy (GitHub Pages):** https://chadyi-king.github.io/mission-control-dashboard/ (deprecated)

**Update Speed:**
- Render: 30 seconds after git push
- GitHub Pages: 10 minutes after git push

## Data Access Reality (IMPORTANT)

**Main Session** (when you chat with me directly):
- ✅ CAN read `/mission-control-dashboard/data.json`
- ✅ CAN verify real task counts, deadlines, agent status
- ✅ CAN check file timestamps and git status

**Cron Jobs** (isolated automated reports):
- ❌ CANNOT access workspace files
- ❌ CANNOT verify dashboard data freshness
- ✅ CAN check `/agents/` directory files only
- ✅ Reports based on accessible agent audit logs, not live data

**Result:** Cron job reports may show stale dates (like "Feb 7") because they can't read the actual data.json. Only trust dashboard data when I report it from the main session.

---

## Heartbeat Schedule

### 🌅 MORNING HEARTBEAT (08:00 AM)
**Checks:**
- [ ] Read actual data.json from workspace
- [ ] Verify `lastUpdated` timestamp is recent
- [ ] Count real tasks: pending, active, review, done
- [ ] Check today's deadlines
- [ ] Summarize for user

**Format:** Concise summary, no emoji spam.

Example:
> Heartbeat - 16:00 SGT: Dashboard live, 72 tasks, A1-1 due tomorrow, Helios running 15-min audits. No issues.

### ☀️ DAYTIME HEARTBEATS (Every 30 min, 08:30-23:30)
**Checks:**
- [ ] Helios data audit complete
- [ ] Helios pinged agents about their tasks
- [ ] Agents reported status back
- [ ] Any urgent deadlines (<24h)?

**Format:** Clean, readable, agents on separate lines.

Example:
```
Heartbeat - 23:30 SGT

Helios has pinged these agents:

CHAD_YI
  Task: Dashboard infrastructure
  Status: Verifying agent audit logs
  State: Active

Escritor
  Task: A2-12 Chapter outline
  Status: Waiting for Caleb's input
  State: Idle 2 days

Quanta
  Task: A5-1 OANDA trading bot
  Status: Needs API credentials
  State: Blocked

MensaMusa
  Task: A5-2 Options monitoring
  Status: Needs Moomoo account
  State: Blocked

Autour
  Task: A3 KOE scripts
  Status: Not yet spawned
  State: Not spawned

Urgent: A1-1 due tomorrow
```

### 🌙 MIDNIGHT HEARTBEAT (00:00)
**Checks:**
- [ ] Day summary: tasks done today
- [ ] Write to memory/YYYY-MM-DD.md
- [ ] Archive logs

---

## Quick Status Check (Manual)

When user asks "what's the status":

```bash
# Read real data
cat mission-control-dashboard/data.json | jq '.stats, .lastUpdated'

# Count actual tasks
cat mission-control-dashboard/data.json | jq '.tasks | length'

# Check deadlines
cat mission-control-dashboard/data.json | jq '.tasks | to_entries[] | select(.value.deadline) | {id: .key, title: .value.title, deadline: .value.deadline}'
```

---

## Current Status (Feb 11, 2026)

**Active Agents:**
- CHAD_YI (Orchestrator) - ✅ Active
- Helios (Mission Control Engineer) - ✅ Active, running 15-min audits
- Escritor (Story Agent) - ⚠️ waiting_for_input

**Configured (Not Spawned):**
- Quanta, MensaMusa (A5 Trading) - blocked, needs credentials
- Autour (A3 KOE) - not spawned

**Task Count:** 47 total (from real data.json)

**Blockers:**
- A5 Trading: needs OANDA + Moomoo credentials

