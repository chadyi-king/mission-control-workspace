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

## Each Heartbeat — What Happens

### Step 1: Prompt Helios to Poke All Agents

I send to Helios inbox:
```bash
/home/chad-yi/.openclaw/workspace/agents/helios/inbox/poke-request-{timestamp}.json
```

Content:
```json
{
  "type": "agent_poke",
  "from": "chad-yi",
  "timestamp": "ISO-8601",
  "request": "Check all agent health and task status",
  "agents_to_check": ["cerebronn", "forger", "quanta", "escritor", "autour", "mensamusa"],
  "report_to": ["chad-yi", "cerebronn"]
}
```

### Step 2: Helios Executes

Helios:
1. Checks systemd status for each agent
2. Reads their current-task.md / state files
3. Verifies they're making progress
4. Detects blockers or silences
5. Generates report

### Step 3: Reports Generated

**Helios sends to my inbox:**
- `helios-report-{timestamp}.json` — Full technical data
- `helios-summary-{timestamp}.md` — Human-readable summary

**Helios sends to Cerebronn inbox:**
- `helios-briefing-{timestamp}.md` — Strategic overview for Brain

### Step 4: I Process Reports

**Quick Check (12pm, 2pm, 4pm, 6pm, 8pm):**
- Read summary
- If all green → HEARTBEAT_OK (or silent)
- If issues → Format concise report for Caleb

**Digest (10am, 10pm):**
- Full analysis
- Task-by-task breakdown
- Agent status section
- Blockers requiring decisions
- Escalations if needed

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

**Current:** Quanta logs to `logs/quanta.log`
**New:** Quanta also writes to `outbox/trade-alert-{timestamp}.json`

**Flow:**
```
Quanta enters trade
    ↓
Writes: outbox/trade-alert-{timestamp}.json
    ↓
Helios detects (during audit) OR I poll every 20 min
    ↓
I read alert immediately
    ↓
Report to Caleb: "Quanta entered XAUUSD BUY at 2950.50"
```

### Quanta Alert File Format

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

Monitoring for exit...
```

### Implementation Options

**Option A: Helios detects (recommended)**
- Helios checks Quanta outbox during audits
- If trade alert found → flags as URGENT to me
- I report to Caleb immediately

**Option B: I poll every 20 min**
- I check `quanta/outbox/` every 20 minutes
- If new trade file → read and report
- Simpler, no Helios changes needed

**Option C: Quanta sends direct (not possible)**
- Quanta can't message Telegram directly
- Would need API integration

**Recommendation: Option B (I poll)**
- No Helios code changes needed
- I control the reporting
- Can verify before alerting (reduce noise)

---

## Communication Flow Summary

### Heartbeat (Every 2h/3h)
```
Chad (me)
    ↓
Send poke request to Helios inbox
    ↓
Helios checks all agents
    ↓
Helios reports to:
    → Chad inbox (summary)
    → Cerebronn inbox (strategic)
    ↓
I format report for Caleb
    ↓
Caleb gets digest (if 10am/10pm) or quick check
```

### Quanta Trade Alert (Immediate)
```
Quanta executes trade
    ↓
Writes trade-alert.json to outbox
    ↓
I poll every 20 min (or detect via Helios)
    ↓
I read alert
    ↓
Report immediately to Caleb
    ↓
Monitor trade until exit
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
| Send poke to Helios | `agents/helios/inbox/poke-request-{ts}.json` |
| Receive Helios report | `agents/chad-yi/inbox/helios-report-{ts}.json` |
| Send brief to Cerebronn | `agents/cerebronn/inbox/task-{ts}.md` |
| Receive Cerebronn response | `agents/chad-yi/inbox/response-{ts}.md` |
| Quanta trade alerts | `agents/quanta/outbox/trade-alert-{ts}.json` |
| My session reports | `agents/cerebronn/inbox/chad-session-{ts}.md` |

---

## Cron/Automation

**Manual for now:** I send heartbeats manually based on schedule
**Future:** Can set up OpenClaw cron for automatic heartbeats

**Quanta polling:** Every 20 min during market hours (London/NY sessions)

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
