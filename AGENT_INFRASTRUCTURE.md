# AGENT_INFRASTRUCTURE.md - Mission Control Agent Coordination System

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CALEB (User)                           │
└─────────────────────────┬───────────────────────────────────┘
                          │ Receives filtered summaries
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHAD_YI (Orchestrator)                   │
│  • Receives compiled reports from Helios                    │
│  • Filters and decides what to escalate                     │
│  • Fixes dashboard/data issues                              │
│  • Messages Caleb only when needed                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ sessions_send (reports)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              HELIOS (Mission Control Engineer)              │
│  • Pings all agents every 15 min: "Status update?"         │
│  • Compiles agent reports into single summary              │
│  • Verifies dashboard accuracy vs reality                  │
│  • Detects discrepancies, tells CHAD_YI what to fix        │
│  • Reports: "Update data.json: Quanta is Active not Blocked"│
└──────┬────────┬────────┬────────┬───────────────────────────┘
       │        │        │        │
       ▼        ▼        ▼        ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  QUANTA │ │ESCRITOR │ │MENSAMUSA│ │ AUTOUR  │
│(Trading)│ │ (Story) │ │(Options)│ │(Content)│
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │
     ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│CallistoFX│ │ A2-13   │ │ Moomoo  │ │  KOE    │
│Signals  │ │ Chapter │ │(blocked)│ │(pending)│
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

---

## 1. HELIOS CORE RESPONSIBILITIES

### 1.1 Agent Status Polling (Every 15 Minutes)

Helios sends structured ping to each agent:
```
sessions_send to={agent}:
"Helios ping [TIMESTAMP]. Please respond with:
1. Current task ID and description
2. Status: active/blocked/waiting/idle
3. Progress % or time spent
4. Any blockers
5. Next milestone ETA"
```

### 1.2 Agent Response Format (Standardized)

All agents MUST respond in this format:
```markdown
## Agent Status Report - [AGENT_NAME]
**Timestamp:** [ISO-8601]
**Task:** [Task ID] - [Brief description]
**Status:** [active/blocked/waiting/idle/not_spawned]
**Progress:** [X%] OR [Time spent: X hours/days]
**Blocker:** [None / Description of what's blocking]
**Next Milestone:** [What happens next and when]
**Notes:** [Any relevant context]
```

### 1.3 Helios Compilation Report to CHAD_YI

After collecting all agent responses, Helios sends:
```markdown
## Helios Agent Coordination Report
**Time:** [TIMESTAMP]

### Agent Status Summary
| Agent | Task | Status | Progress | Blocker | Action Needed |
|-------|------|--------|----------|---------|---------------|
| CHAD_YI | A6-3 | Active | - | None | - |
| Escritor | A2-13 | Active | 60% | None | - |
| Quanta | A5-1 | Active | Monitoring | None | - |
| MensaMusa | A5-2 | Blocked | - | Moomoo credentials | Provide credentials |
| Autour | - | Not Spawned | - | - | Spawn when ready |

### Critical Updates
- [Any urgent items]

### Dashboard Discrepancies
- data.json shows: [X]
- Reality: [Y]
- Fix needed: [Specific action]

### Next Audit: [+15 min timestamp]
```

---

## 2. QUANTA SPECIFIC INTEGRATION

### 2.1 Signal Detection and Reporting

When Quanta captures a CallistoFX signal:

**Step 1:** Parse signal immediately
**Step 2:** Write to `/agents/quanta/signals/PENDING/{signal_id}.json`
**Step 3:** Send alert to Helios:
```
sessions_send to=helios:
"NEW SIGNAL CAPTURED:
- Pair: XAUUSD
- Direction: BUY
- Entry: 2680-2685
- SL: 2675
- TPs: 2700/2720/2740/2760/2780
- Confidence: [calculated]
- Time: [timestamp]"
```

### 2.2 Helios Processes Signal Alert

Helios includes in next report to CHAD_YI:
```markdown
### Trading Signal Alert
**Quanta detected new CallistoFX signal:**
- XAUUSD BUY 2680-2685
- Target: 2700/2720/2740/2760/2780
- SL: 2675
- Current price: [fetched from OANDA]
- Distance to entry: [X pips]
- Status: [Waiting for entry / Executed / Expired]

**Context:**
- Quanta is monitoring for entry
- Will execute 3-tier DCA if price hits range
- Risk: $20 fixed

**Action Required:** None (automated) / Manual approval needed
```

### 2.3 Post-Trade Reporting

After trade execution:
- Quanta writes trade log
- Updates P&L summary
- Helios includes in next report: "Trade executed, position open, P&L: +X"

---

## 3. AGENT COORDINATION WORKFLOW

### 3.1 Standard 15-Minute Cycle

```
T+0:00  Helios sends pings to all agents
T+0:02  Agents respond with status reports
T+0:05  Helios compiles and verifies dashboard
T+0:07  Helios sends compiled report to CHAD_YI
T+0:10  CHAD_YI reviews and fixes any issues
T+0:15  Cycle repeats
```

### 3.2 Event-Driven Triggers

**Immediate triggers (outside 15-min cycle):**
- Quanta captures signal → Immediate alert to Helios
- Agent becomes blocked → Immediate alert
- Critical deadline <4 hours → Immediate alert
- Trade executed → Log update

### 3.3 Dashboard Verification Process

Helios verifies dashboard accuracy:

1. **Read data.json** - Get agent statuses from dashboard
2. **Read agent files** - Get actual agent states
3. **Compare:**
   - data.json says Quanta = "Blocked"
   - Quanta files say = "Active, OANDA connected"
   - **DISCREPANCY DETECTED**
4. **Tell CHAD_YI:** "Fix needed: Update data.json agentDetails.quanta.state from 'Blocked' to 'Active'"
5. **CHAD_YI fixes**
6. **Next cycle:** Helios verifies fix applied

---

## 4. COMMUNICATION PROTOCOL

### 4.1 Message Bus Structure

```
/agents/message-bus/
├── inbox/
│   ├── helios/          # Agents drop reports here
│   ├── chad_yi/         # Helios drops compiled reports
│   └── broadcast/       # Urgent alerts
├── outbox/              # Agents write their own updates
└── archive/             # Old messages
```

### 4.2 Communication Rules

| From | To | Channel | When |
|------|-----|---------|------|
| Helios | Agents | sessions_send | Every 15 min (ping) |
| Agents | Helios | sessions_send | Response to ping OR event |
| Helios | CHAD_YI | sessions_send | Compiled reports |
| Quanta | Helios | sessions_send | New signals immediately |
| CHAD_YI | Caleb | message tool | Only when escalating |

### 4.3 Priority Levels

**IMMEDIATE (alert within 1 min):**
- Critical task deadline today
- Large trading loss
- System failure

**HIGH (alert within 15 min):**
- New trading signal
- Agent blocked >24h
- Deadline tomorrow

**NORMAL (15-min cycle):**
- Regular status updates
- Progress reports
- Dashboard discrepancies

**LOW (daily digest):**
- Completed tasks summary
- P&L summaries
- General progress

---

## 5. HELIOS IMPLEMENTATION SPECIFICATION

### 5.1 Helios Agent Configuration

```yaml
agent: helios
role: mission_control_engineer
schedule:
  - every: 15 minutes
    action: ping_all_agents
  - every: 15 minutes
    action: verify_dashboard
  - on_event: signal_detected
    action: immediate_alert
tasks:
  - name: agent_coordination
    description: Ping agents, compile reports
  - name: dashboard_audit
    description: Verify data.json accuracy
  - name: discrepancy_detection
    description: Find and report mismatches
  - name: escalation_filter
    description: Tell CHAD_YI what needs fixing
```

### 5.2 Helios Skill Requirements

**Tools needed:**
- `read` - Agent files, data.json
- `write` - Audit logs, reports
- `sessions_send` - Message agents and CHAD_YI
- `sessions_list` - Check agent sessions
- `browser` - Screenshot dashboard for verification
- `exec` - Git status checks

**Skills:**
- `helios-audit` (existing)
- File monitoring
- Data comparison
- Report generation

### 5.3 Helios State Management

Helios maintains state in:
- `/agents/helios/AGENT_STATE.json` - His config
- `/agents/helios/outbox/` - Audit logs
- `/agents/message-bus/outbox/helios/` - Reports to CHAD_YI

---

## 6. AGENT INTEGRATION SPECIFICATIONS

### 6.1 Quanta Integration

**Files Quanta maintains:**
- `current-task.md` - Current status
- `signals/PENDING/` - Active signals
- `signals/EXECUTED/` - Completed trades
- `logs/daily_pnl.md` - Daily P&L

**Quanta alerts Helios when:**
- New signal captured
- Trade executed
- Position closed
- Error/failure

### 6.2 Escritor Integration

**Files Escritor maintains:**
- `current-task.md` - Chapter progress
- `outbox/drafts/` - Completed chapters
- `MEMORY.md` - Story bible updates

**Escritor alerts Helios when:**
- Chapter draft complete
- Blocked (needs Caleb input)
- Story bible updated

### 6.3 MensaMusa Integration

**Files MensaMusa maintains:**
- `current-task.md` - Status
- `logs/options_flow.md` - Monitored flows

**MensaMusa alerts Helios when:**
- Blocker resolved
- Options flow detected
- Ready to trade

### 6.4 Autour Integration

**Files Autour maintains:**
- `current-task.md` - Script status
- `outbox/scripts/` - Completed scripts

**Autour alerts Helios when:**
- Script draft complete
- Blocked (needs direction)

---

## 7. DASHBOARD VERIFICATION PROTOCOL

### 7.1 What Helios Checks

**Every 15 minutes:**
1. Read `data.json` - Extract agent statuses
2. Read each agent's `current-task.md` - Get actual status
3. Compare values
4. Detect discrepancies

**Discrepancy Examples:**
| Dashboard | Reality | Fix |
|-----------|---------|-----|
| Quanta: Blocked | Quanta: Active, trading | Update data.json |
| Escritor: Idle | Escritor: Writing chapter | Update data.json |
| Task count: 71 | Git shows 72 | Recount and update |

### 7.2 How Helios Reports Discrepancies

```
sessions_send to=chad_yi:
"DASHBOARD DISCREPANCY DETECTED:

File: data.json
Path: agentDetails.quanta.state
Current: 'Blocked'
Should be: 'Active'
Reason: OANDA credentials configured, ready for trading

Fix: Edit data.json line X, change 'Blocked' to 'Active'

Verification: After fix, Helios will confirm next cycle."
```

---

## 8. DAILY DIGEST PROTOCOL

### 8.1 End-of-Day Summary (8 PM SGT)

Helios compiles and sends to CHAD_YI:
```markdown
## Daily Digest - [DATE]

### Tasks Completed Today
- [Task ID]: [Description] by [Agent]

### Tasks In Progress
- [Task ID]: [X%] by [Agent]

### Blockers
- [Agent]: [Blocker description]

### Trading Summary (Quanta)
- Trades executed: [N]
- P&L: [+/-$X]
- Open positions: [N]

### Tomorrow's Priorities
1. [Task] - [Deadline]
2. [Task] - [Deadline]

### Dashboard Health
- Discrepancies fixed: [N]
- Current status: ✅ Clean / ⚠️ Issues
```

### 8.2 CHAD_YI Filters for Caleb

CHAD_YI decides what Caleb sees:
- Blockers requiring Caleb's decision
- Critical deadline alerts
- Trading summaries
- Completed milestones

---

## 9. IMPLEMENTATION PHASES

### Phase 1: Core Infrastructure (This Session)
1. ✅ Write AGENT_INFRASTRUCTURE.md (this file)
2. Set up `/agents/message-bus/` structure
3. Create agent response templates
4. Configure Helios agent with full specification

### Phase 2: Helios Deployment (Today)
1. Spawn autonomous Helios with this specification
2. Test ping/response cycle with all agents
3. Verify dashboard audit works
4. Test signal flow from Quanta

### Phase 3: Agent Integration (This Week)
1. Quanta: Full signal reporting
2. Escritor: Progress reporting
3. MensaMusa: Status (when unblocked)
4. Autour: Setup (when spawned)

### Phase 4: Daily Operations (Ongoing)
1. 15-minute cycles running
2. Daily digests at 8 PM
3. Continuous dashboard verification
4. Event-driven alerts

---

## 10. SUCCESS METRICS

- **Issue detection → Report:** < 15 minutes
- **Agent ping → Response:** < 2 minutes
- **Signal capture → Alert:** < 30 seconds
- **Dashboard discrepancy → Fix:** < 30 minutes
- **Daily digest delivery:** 8 PM ± 5 min
- **False positive rate:** < 5%

---

## 11. FILES TO CREATE/MODIFY

### New Files
- `/AGENT_INFRASTRUCTURE.md` (this file)
- `/agents/message-bus/inbox/` structure
- `/agents/quanta/signals/` structure
- Agent response templates

### Modified Files
- `/agents/helios/AGENT_STATE.json` - Update with full config
- `/skills/helios-audit/SKILL.md` - Add coordination protocols

---

*Infrastructure Plan Complete - Ready for Implementation*
