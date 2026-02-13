# AGENT_PLAN.md - Mission Control Agent Architecture

## Overview
Proposed multi-agent system for autonomous task execution and reporting to Caleb.

---

## Agent Roles

### 1. CHAD_YI (Orchestrator) - YOU
**Status:** Active  
**Role:** CEO/Brain, human interface, strategic decisions  
**Responsibilities:**
- Receive consolidated reports from agents
- Make strategic decisions
- Spawn/terminate agents as needed
- Only agent that messages Caleb directly

### 2. Helios (Mission Control Engineer)
**Status:** Cron-only (needs upgrade)  
**Proposed Role:** Autonomous auditor and coordinator  
**Responsibilities:**
- Audit dashboard/data integrity every 15 min
- Monitor agent health and task progress
- **Report TO CHAD_YI** (not Caleb directly)
- Flag blockers, stale tasks, data issues
- Coordinate fixes with CHAD_YI

**Reporting Flow:**
```
Finds Issue → Reports to CHAD_YI → CHAD_YI fixes or escalates to Caleb
```

### 3. Quanta (Trading Dev)
**Status:** Active (OANDA connected)  
**Role:** Trading algorithm execution  
**Responsibilities:**
- Monitor CallistoFX signals
- Execute trades via OANDA
- Manage positions (3-tier DCA, TP/SL)
- Log all trades
- **Report TO CHAD_YI:** Daily P&L, trade summaries, issues

**Reporting:**
- Immediate: Trade executions (via logs)
- Daily: P&L summary to CHAD_YI
- Urgent: Blocked (API down, large loss) → CHAD_YI → Caleb

### 4. Escritor (Story Agent)
**Status:** Active (A2-13 Study Phase)  
**Role:** RE:UNITE novel writing  
**Responsibilities:**
- Weekly chapter drafts
- Story Bible maintenance
- Character/world building
- **Report TO CHAD_YI:** Weekly progress, drafts ready for review

**Reporting:**
- Weekly: Chapter progress
- Blocked: Needs Caleb input → CHAD_YI → Caleb

### 5. MensaMusa (Options Trading)
**Status:** Configured, not spawned  
**Role:** Options flow monitoring  
**Blocked:** Needs Moomoo credentials  
**Responsibilities:** (when unblocked)
- Monitor Twitter/options flow
- Execute options trades via Moomoo
- **Report TO CHAD_YI:** Daily positions, unusual activity

### 6. Autour (Content Creator)
**Status:** Configured, not spawned  
**Role:** KOE YouTube/TikTok scripts  
**Responsibilities:**
- Script writing for political/spiritual content
- **Report TO CHAD_YI:** Draft scripts for approval

---

## Communication Protocol

### Rule 1: No Agent Messages Caleb Directly
Only CHAD_YI messages Caleb. All agents report to CHAD_YI.

### Rule 2: Escalation Levels
```
Level 1: Agent finds issue → Reports to CHAD_YI
Level 2: CHAD_YI fixes or decides to escalate
Level 3: CHAD_YI messages Caleb (if needed)
```

### Rule 3: Urgent Override
If CHAD_YI is unavailable >2 hours, Helios can send urgent alert to Caleb for:
- Critical deadline missed
- System down
- Large trading loss
- Security issue

### Rule 4: Daily Digest (Not Spam)
Instead of constant messages, daily summary at 8 PM SGT:
- Tasks completed today
- Blockers needing attention
- Tomorrow's priorities

---

## Helios Upgrade Plan

### Current State
- Cron job every 15 min
- Writes JSON audit files
- No proactive reporting
- Issues sit undetected

### Proposed Upgrade
Spawn autonomous Helios agent that:
1. Self-triggers every 15 min via heartbeat
2. Reads audit files, analyzes issues
3. **Sends message to CHAD_YI** via `sessions_send` when issues found
4. Collaborates with CHAD_YI on fixes
5. Reports fix status

**Helios Skills Needed:**
- `helios-audit` (already exists)
- File reading (data.json, agent files)
- Messaging (sessions_send to CHAD_YI)
- Screenshot (browser for visual verification)

### Helios Daily Schedule
```
:00 - Audit data.json integrity
:15 - Check agent health (all 5 agents)
:30 - Verify dashboard rendering (screenshot)
:45 - Review CHAD_YI's task progress
:00 - Loop
```

---

## Implementation Phases

### Phase 1: Helios Upgrade (Week 1)
- [ ] Spawn autonomous Helios agent
- [ ] Test reporting to CHAD_YI
- [ ] Verify escalation to Caleb works
- [ ] Run parallel with cron for 1 week

### Phase 2: Quanta Automation (Week 2)
- [ ] Ensure Quanta logs are readable
- [ ] Set up daily P&L reports to CHAD_YI
- [ ] Test urgent alert flow (simulated)

### Phase 3: Escritor Integration (Week 3)
- [ ] Weekly progress reports to CHAD_YI
- [ ] Blocker escalation when waiting for Caleb

### Phase 4: Remaining Agents (As Needed)
- [ ] MensaMusa (when Moomoo ready)
- [ ] Autour (when KOE priority)

---

## Success Metrics

1. **Issues detected → reported < 15 minutes**
2. **No Caleb message unless CHAD_YI escalates**
3. **Daily digest sent reliably at 8 PM**
4. **Blockers unblocked within 24 hours**

---

## Open Questions

1. Do you want the daily digest, or prefer on-demand status checks?
2. Should Helios ping you for ALL issues, or only critical/high priority?
3. Do you want to approve this plan before I spawn Helios autonomous agent?
4. Any other agents you want included in the plan?

---

*Draft v1.0 - Awaiting Caleb's approval*
