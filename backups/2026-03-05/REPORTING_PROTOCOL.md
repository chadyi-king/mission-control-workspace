# CHAD_YI Reporting Protocol — Heartbeat & Digest System

## Heartbeat Schedule (Caleb Requested)

### Daytime Heartbeats (Every 2 hours)
| Time | Type | Purpose |
|------|------|---------|
| 10:00 | **MORNING DIGEST** | Extensive, full system status |
| 12:00 | Quick Check | Agent poke + task status |
| 14:00 | Quick Check | Agent poke + task status |
| 16:00 | Quick Check | Agent poke + task status |
| 18:00 | Quick Check | Agent poke + task status |
| 20:00 | Quick Check | Agent poke + task status |
| 22:00 | **NIGHT DIGEST** | Extensive, full system status |

### Nighttime Heartbeats (Every 3 hours)
| Time | Type | Purpose |
|------|------|---------|
| 01:00 | Silent Check | Agent health only (no report unless issue) |
| 04:00 | Silent Check | Agent health only (no report unless issue) |
| 07:00 | Silent Check | Agent health only (no report unless issue) |

---

## Each Heartbeat — What Actually Happens

### Understanding Helios's Role

**Helios already runs 15-minute audits automatically where he:**
1. Pokes all agents (checks if they're alive)
2. Updates dashboard (ACTIVE.md → data.json → git push)
3. Detects discrepancies and silences
4. Writes audit reports

**My heartbeat prompts Helios to do a COMPREHENSIVE audit and REPORT BACK.**

### Step 1: I Prompt Helios for Full Report

I send to Helios inbox:
```bash
/home/chad-yi/.openclaw/workspace/agents/helios/inbox/heartbeat-request-{timestamp}.json
```

Content:
```json
{
  "type": "comprehensive_audit",
  "from": "chad-yi",
  "timestamp": "ISO-8601",
  "request": "Run full system audit and compile report",
  "scope": [
    "agent_health_status",
    "dashboard_data_integrity", 
    "task_progress_check",
    "blocker_identification",
    "quanta_trade_monitoring"
  ],
  "report_to": ["chad-yi", "cerebronn"],
  "priority": "normal"
}
```

### Step 2: Helios Does His Job

**Helios executes his standard 15-minute cycle PLUS comprehensive checks:**

1. **Pokes all agents** (his normal job)
   - Checks systemd status
   - Reads current-task.md files
   - Verifies progress

2. **Updates dashboard** (his normal job)
   - Reads ACTIVE.md
   - Writes data.json
   - Git commit + push
   - Render deploys

3. **Compiles comprehensive report** (triggered by my request)
   - All agent statuses
   - Task blockers
   - Dashboard sync status
   - Quanta trade alerts (if any)

### Step 3: Helios Sends Reports

**To my inbox:**
- `helios-audit-{timestamp}.json` — Full technical data
- `helios-summary-{timestamp}.md` — Human-readable summary

**To Cerebronn inbox:**
- `helios-briefing-{timestamp}.md` — Strategic overview for Brain

### Step 4: I Format for Caleb

**Quick Check (12pm, 2pm, 4pm, 6pm, 8pm):**
- Read Helios summary
- If all green → Silent or brief acknowledgment
- If issues → Concise report for Caleb

**Digest (10am, 10pm):**
- Full analysis of Helios report
- Task breakdown
- Agent status
- Blockers
- Escalations

---

## Report Templates

### Quick Check Report (to Caleb)

```
Heartbeat — 14:00 SGT

Tasks
• Active: 6 | Review: 1 | Blocked: 4
• 🔴 A1-6: Lisa contract — OVERDUE
• 🟡 B6-8: Gel blitz guns — Due tomorrow

Agents
• Helios ✅ | Monitoring
• Cerebronn ✅ | Cycle #22
• Forger ✅ | 4 builds pending
• Quanta ✅ | 0 active trades

Blockers
• A1-6: Need you to sign contract

No action needed unless you want to address A1-6.
```

### Morning/Night Digest (Extensive)

```markdown
# Mission Control Digest — 10:00 SGT

## Task Overview
| Status | Count | IDs |
|--------|-------|-----|
| 🔴 Critical | 4 | A1-6, A1-5, B6-8, A1-2 |
| 🟡 Urgent | 3 | B6-7, B8-6, A6-15 |
| 🟢 Active | 2 | A5-1, A5-3 |
| 🟣 Review | 1 | A6-15 |
| ✅ Done (24h) | 3 | — |

## Detailed Task Status

### 🔴 Critical (Needs Action)
| ID | Task | Owner | Deadline | Blocker |
|----|------|-------|----------|---------|
| A1-6 | Sign Lisa's contract | CHAD_YI | TODAY | Waiting for signature |
| A1-5 | Rebook ACLP | CHAD_YI | Tomorrow | — |
| B6-8 | Gel blitz guns | CHAD_YI | Tuesday | — |
| A1-2 | Findit payment | CHAD_YI | Friday | — |

### 🟡 Urgent (This Week)
| ID | Task | Owner | Deadline | Status |
|----|------|-------|----------|--------|
| B6-7 | SMU insurance | CHAD_YI | Friday | Moved to Friday |
| B8-6 | Andre's video | CHAD_YI | Sunday | Changes needed |
| A6-15 | Dashboard audit | Helios | REVIEW | Awaiting approval |

### 🟢 Active (In Progress)
| ID | Task | Owner | Progress |
|----|------|-------|----------|
| A5-1 | Quanta testing | Quanta | Live trading, 0 positions |
| A5-3 | Symbol list update | CHAD_YI | In progress |

## Agent Status

| Agent | Status | Current Task | Health |
|-------|--------|--------------|--------|
| **Helios** | ✅ Running | 15-min audits, dashboard sync | 18h uptime |
| **Cerebronn** | ✅ Running | Cycle #22, briefing updates | 17h uptime |
| **Forger** | ✅ Running | 4 pending builds | 17h uptime |
| **Quanta** | ✅ Running | Monitoring, 0 trades | 12h uptime (fixed) |
| **Escritor** | 💤 Dormant | — | Intentional |
| **Autour** | 💤 Dormant | — | Intentional |
| **MensaMusa** | 💤 Dormant | — | Intentional |

## Blockers Requiring Decisions

1. **A1-6: Lisa's contract**
   - Status: OVERDUE
   - Need: Your signature
   - Impact: Blocking onboarding
   - Decision needed: Sign today?

2. **B6 Elluminate website**
   - Status: Forger has brief but unclear
   - Need: Specific requirements from you
   - Impact: Blocking B6 launch
   - Decision needed: Approve Forger to build?

3. **Quanta stability**
   - Status: Fixed (lock file cleared)
   - Risk: Could crash again
   - Need: Permanent fix or monitoring
   - Decision needed: Accept terminal mode or fix service?

## Decisions Made (Last 12h)

| Decision | By | Impact |
|----------|-----|--------|
| Cleared Quanta lock file | Chad | Service stable |
| Verified Helios sync | Chad | Dashboard updating |

## Upcoming (Next 12h)

| Time | Event |
|------|-------|
| 12:00 | Heartbeat check |
| 14:00 | Heartbeat check |
| 16:00 | Heartbeat check |

## Escalations for Caleb

None — all blockers listed above. Reply if you want me to action any.
```

---

## Quanta Immediate Trade Alerts

### How It Works

**Helios checks Quanta during his 15-minute audits:**

```
Helios 15-min audit cycle
    ↓
Checks Quanta service status
    ↓
Reads Quanta outbox for trade alerts
    ↓
If trade alert found → Flags as URGENT
    ↓
Sends to my inbox immediately
    ↓
I report to Caleb: "Quanta entered XAUUSD BUY at 2950.50"
```

### Quanta Trade Alert Format

Quanta writes to: `agents/quanta/outbox/trade-alert-{timestamp}.json`

```json
{
  "type": "trade_executed",
  "timestamp": "2026-03-02T22:15:00+08:00",
  "agent": "quanta",
  "trade": {
    "symbol": "XAUUSD",
    "direction": "BUY",
    "entry_price": 2950.50,
    "stop_loss": 2945.00,
    "take_profit": [2960.00, 2970.00],
    "position_size": 0.1,
    "trade_id": "Q-20260302-001"
  },
  "signal_source": "CallistoFX",
  "risk_percent": 1.0
}
```

### Helios Detection

**During 15-min audit, Helios:**
1. Checks if `quanta/outbox/trade-alert-*.json` exists
2. If found → Reads and validates
3. Writes URGENT alert to my inbox: `URGENT-quanta-trade-{timestamp}.md`
4. Includes in next audit report

### My Immediate Report to Caleb

**Format:**
```
🚨 QUANTA TRADE EXECUTED

Trade: BUY XAUUSD @ 2950.50
Size: 0.1 lots
SL: 2945.00 | TP: 2960.00 / 2970.00
Risk: 1% of account
Signal: CallistoFX (message 53385)
Time: 22:15 SGT
Trade ID: Q-20260302-001

Monitoring for exit...
```

### Timeline

| Event | Time |
|-------|------|
| Quanta enters trade | T+0 |
| Quanta writes alert | T+0 |
| Helios detects (next 15-min audit) | T+0 to T+15 min |
| Helios sends URGENT to me | T+0 to T+15 min |
| I report to Caleb | Within 5 min of receiving |
| **Max delay** | **~20 minutes** |

If immediate alert needed (< 5 min), I can poll Quanta outbox every 5 minutes during active trading sessions.

---

## Communication Flow Summary

### Heartbeat (Every 2h/3h)
```
Chad (me)
    ↓
Send heartbeat request to Helios inbox
    ↓
Helios runs comprehensive audit:
    - Pokes all agents (his normal 15-min job)
    - Updates dashboard (ACTIVE.md → data.json → git push)
    - Checks for blockers
    - Compiles report
    ↓
Helios sends reports:
    → Chad inbox (summary for me)
    → Cerebronn inbox (strategic for Brain)
    ↓
I format report for Caleb
    ↓
Caleb gets digest (10am/10pm) or quick check
```

### Quanta Trade Alert (Within 15 min)
```
Quanta executes trade
    ↓
Writes trade-alert.json to outbox
    ↓
Helios detects (during next 15-min audit)
    ↓
Helios sends URGENT to my inbox
    ↓
I report immediately to Caleb
    ↓
Monitor trade until exit
```

### Routine Monitoring (Helios Auto)
```
Helios runs every 15 minutes automatically
    ↓
Pokes all agents
Updates dashboard
Checks Quanta for trades
    ↓
If issues found → URGENT to me
If normal → logs only
```

### Cerebronn Coordination (Async)
```
I need strategic decision
    ↓
Write brief to Cerebronn inbox
    ↓
Caleb prompts Cerebronn in VS Code
    ↓
Cerebronn responds to my inbox
    ↓
I act on decision
```

---

## Files & Paths

| Purpose | Path |
|---------|------|
| Send heartbeat to Helios | `agents/helios/inbox/heartbeat-request-{ts}.json` |
| Receive Helios report | `agents/chad-yi/inbox/helios-audit-{ts}.json` |
| Send brief to Cerebronn | `agents/cerebronn/inbox/task-{ts}.md` |
| Receive Cerebronn response | `agents/chad-yi/inbox/response-{ts}.md` |
| Quanta trade alerts | `agents/quanta/outbox/trade-alert-{ts}.json` |
| My session reports | `agents/cerebronn/inbox/chad-session-{ts}.md` |

---

## Cron/Automation

**Manual for now:** I send heartbeats manually based on schedule
**Future:** Can set up OpenClaw cron for automatic heartbeats

**Quanta trade detection:** Helios checks during 15-min audits (max 15 min delay)

---

## Key Rules

1. **Only escalate to Caleb if:**
   - Task is overdue and blocked on him
   - Agent crash I can't fix
   - Decision needed with no clear answer
   - Quanta trade entered (always report)

2. **Report to Cerebronn when:**
   - Strategic decisions needed
   - Multi-agent coordination required
   - Architecture questions
   - End of session summary

3. **Silent mode:**
   - Night checks (1am, 4am, 7am) — only alert if critical
   - Quanta no-trade periods — just log, don't report

---

*Protocol established: March 2, 2026*
*Next review: When schedule needs adjustment*
