# MASTER PLAN: Kimi-Claw-Helios Integration
## Mission Control System v3.0

**Date:** February 16, 2026
**Goal:** Autonomous, self-managing agent collaboration between CHAD_YI and Kimi-Claw-Helios
**Status:** Planning Phase

---

## EXECUTIVE SUMMARY

**Current State:**
- CHAD_YI (OpenClaw): Has memory, orchestration, decision-making
- Helios (current): Basic monitoring, many issues
- Kimi-Claw-Helios (new): Cloud-based, browser automation capable
- Communication: Not yet established

**Target State:**
- CHAD_YI: Strategic orchestrator, maintains memory, makes decisions
- Kimi-Claw-Helios: 24/7 executor, browser automation, autonomous monitoring
- Communication: Seamless, event-driven, zero manual intervention
- You: Set direction, receive reports, intervene only when needed

---

## PHASE 1: PRE-CONNECTION PREP (You do this)

### 1.1 Kimi-Claw-Helios Setup Checklist

**Step 1: Create Kimi Claw Instance**
```
□ Go to https://www.kimi.com/bot
□ Create new instance: "Kimi-Claw-Helios"
□ Enable 24/7 mode
□ Note the instance URL/IP
```

**Step 2: Install Required Skills**
```bash
# In Kimi Claw terminal:
clawhub install screenshot
clawhub install browser
clawhub install file-read
clawhub install telegram
clawhub install system-monitor
clawhub install cron
```

**Step 3: Configure Memory Files**
```
Create in Kimi workspace:
□ AGENTS.md - Copy from CHAD_YI's workspace
□ HEARTBEAT.md - Audit checklist
□ TELEGRAM_CONFIG.md - CallistoFX monitoring
□ DASHBOARD.md - URLs and access info
□ COMMUNICATION_PROTOCOL.md - How to talk to CHAD_YI
```

**Step 4: Telegram Setup**
```
□ Get bot token from @BotFather
□ Add bot to your Telegram
□ Test: Send message to yourself
□ Create group "Mission Control" (optional)
```

**Step 5: File System Access**
```
□ Ensure Kimi can access shared workspace:
  /home/chad-yi/.openclaw/workspace/
□ Test: Create file from Kimi, read from host
```

### 1.2 Network Configuration (CRITICAL)

**Option A: Direct HTTP (Preferred if possible)**
```
□ Kimi binds to 0.0.0.0:8888 (not 127.0.0.1)
□ Windows Firewall allows port 8888
□ CHAD_YI can POST to Kimi's IP
□ Kimi can POST to CHAD_YI's IP
□ Test: curl from each to the other
```

**Option B: Shared File System (Fallback)**
```
□ Mount shared folder both can access
□ CHAD_YI writes to: /shared/tasks/
□ Kimi writes to: /shared/results/
□ Use inotify for instant notification
```

**Option C: Telegram Bridge (Most Reliable)**
```
□ Both agents have Telegram
□ Group chat for coordination
□ Events trigger messages
□ No network configuration needed
```

### 1.3 Secrets & Credentials

**Kimi Claw needs:**
```
□ Telegram bot token
□ Dashboard URL (public)
□ File system paths
□ No OANDA credentials (CHAD_YI handles trading)
```

**CHAD_YI keeps:**
```
□ OANDA API key
□ All trading credentials
□ Memory files
□ Decision-making authority
```

---

## PHASE 2: ARCHITECTURE DESIGN

### 2.1 Role Definitions

**CHAD_YI - The Brain**
```yaml
Responsibilities:
  - Maintain long-term memory
  - Make strategic decisions
  - Execute OANDA trades
  - Update Mission Control dashboard
  - Coordinate multi-agent tasks
  - Handle complex logic
  - Communicate with human (you)

Limitations:
  - No browser automation
  - No 24/7 persistence
  - WSL2 constraints

When to use:
  - Trading decisions
  - Task orchestration
  - Memory updates
  - Complex analysis
```

**Kimi-Claw-Helios - The Eyes & Hands**
```yaml
Responsibilities:
  - 24/7 monitoring
  - Screenshot dashboard
  - Browser automation
  - Telegram Web monitoring (CallistoFX)
  - Detect trading signals
  - Simple data collection
  - Immediate alerting

Limitations:
  - No long-term memory
  - No decision-making
  - No trading execution

When to use:
  - Continuous monitoring
  - Signal detection
  - Browser tasks
  - Data collection
```

### 2.2 Communication Protocol

**Event Types:**

```yaml
Event: trading_signal_detected
From: Kimi
To: CHAD_YI
Priority: CRITICAL
Data:
  symbol: XAUUSD
  direction: BUY
  entry: "4970-4975"
  sl: "4965"
  tps: [4990, 5000, 5010, 5020]
  screenshot: "/path/to/ss.png"
  timestamp: "2026-02-16T15:30:00Z"
Action: CHAD_YI decides execute/skip

---

Event: dashboard_stale
From: Kimi
To: CHAD_YI
Priority: WARNING
Data:
  lastUpdated: "2026-02-16T14:00:00Z"
  currentTime: "2026-02-16T15:30:00Z"
  staleMinutes: 90
Action: CHAD_YI investigates, fixes

---

Event: agent_down
From: Kimi
To: CHAD_YI
Priority: WARNING
Data:
  agent: "quanta"
  lastSeen: "2026-02-15T10:00:00Z"
  status: "process_not_found"
Action: CHAD_YI decides restart/archive

---

Event: task_assigned
From: CHAD_YI
To: Kimi
Priority: NORMAL
Data:
  task_id: "A6-15"
  action: "screenshot_dashboard"
  deadline: "2026-02-16T16:00:00Z"
Action: Kimi executes, reports back

---

Event: task_completed
From: Kimi
To: CHAD_YI
Priority: NORMAL
Data:
  task_id: "A6-15"
  result: "/path/to/screenshot.png"
  status: "success"
Action: CHAD_YI updates dashboard
```

**Communication Methods (Priority Order):**

1. **HTTP POST** (if network allows)
   - Instant
   - Reliable
   - Requires network configuration

2. **Telegram Messages** (recommended)
   - No network setup
   - Persistent history
   - Both agents can participate
   - You can observe

3. **File Events** (fallback)
   - Works across network boundaries
   - Requires polling or inotify
   - Slight delay

4. **Shared Database** (future)
   - SQLite or similar
   - Both read/write
   - Transaction safe

### 2.3 Autonomous Workflows

**Workflow 1: Trading Signal Detection & Execution (FULLY AUTONOMOUS)**

```
┌─────────────────┐
│  CallistoFX     │
│  Telegram       │
└────────┬────────┘
         │ New signal posted
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Kimi-Claw-      │────▶│ CHAD_YI         │
│ Helios          │     │ (Decision)      │
│ - Detects       │     │ - Check OANDA   │
│ - Screenshots   │     │ - Calc size     │
│ - Parses        │     │ - Decide        │
│ - Alerts        │     └────────┬────────┘
└─────────────────┘              │
                                 │ Execute?
                                 ▼
                          ┌──────────────┐
                          │ OANDA        │
                          │ Trade        │
                          └──────────────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ Update       │
                          │ Dashboard    │
                          └──────────────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ Report to    │
                          │ You          │
                          └──────────────┘
```

**Timeline:**
- T+0s: Signal posted
- T+2s: Kimi detects
- T+3s: CHAD_YI receives
- T+5s: CHAD_YI decides
- T+8s: Trade executed
- T+10s: Dashboard updated
- T+12s: You notified

**Your involvement:** None (unless you want to approve first)

---

**Workflow 2: Agent Health Monitoring (AUTONOMOUS)**

```
Every 15 minutes:

Kimi-Claw-Helios:
  1. Screenshot dashboard
  2. Read actual data.json
  3. Check agent processes
  4. Verify timestamps
  5. Compare expected vs actual

If discrepancy found:
  → Alert CHAD_YI with details
  → CHAD_YI investigates
  → CHAD_YI fixes
  → CHAD_YI confirms

If no issues:
  → Log to file (no alert)
```

---

**Workflow 3: Task Assignment (SEMI-AUTONOMOUS)**

```
You: "I need a screenshot of CallistoFX every 2 minutes"
  ↓
CHAD_YI: Creates task A6-15
  ↓
CHAD_YI: Assigns to Kimi
  ↓
Kimi: Executes every 2 min
  ↓
Kimi: Reports results
  ↓
CHAD_YI: Updates status
  ↓
You: See results in dashboard
```

---

## PHASE 3: MEMORY MANAGEMENT

### 3.1 What Each Agent Remembers

**CHAD_YI (Persistent):**
```
MEMORY.md
├── Project descriptions
├── Key decisions
├── Agent configurations
├── Communication protocols
├── User preferences
└── Lessons learned

daily_logs/
├── 2026-02-16.md
├── 2026-02-17.md
└── ...

tasks/
└── [task files]
```

**Kimi-Claw-Helios (Ephemeral):**
```
Runtime only:
├── Current task
├── Recent screenshots
└── Temporary cache

Reloads from:
├── AGENTS.md (static config)
├── HEARTBEAT.md (checklist)
└── CHAD_YI instructions (events)
```

### 3.2 Knowledge Sync Protocol

**When Kimi starts up:**
```
1. Read AGENTS.md (static)
2. Read HEARTBEAT.md (procedures)
3. Request current state from CHAD_YI
4. CHAD_YI sends: active tasks, priorities, blockers
5. Kimi begins operations
```

**When CHAD_YI learns something new:**
```
1. Update MEMORY.md
2. If relevant to Kimi, send notification
3. Kimi updates local config if needed
```

### 3.3 State Reconstruction

**If Kimi crashes/restarts:**
```
1. Auto-restart (cloud)
2. Read static configs
3. Query CHAD_YI: "What should I be doing?"
4. CHAD_YI sends current tasks
5. Resume operations
```

**If CHAD_YI restarts:**
```
1. Read MEMORY.md
2. Check for messages from Kimi
3. Process pending events
4. Resume orchestration
```

---

## PHASE 4: ERROR HANDLING & FALLBACKS

### 4.1 Failure Scenarios

**Scenario 1: Kimi Can't Reach Telegram Web**
```
Detection: Screenshot fails / Login expired
Action:
  1. Kimi alerts CHAD_YI
  2. CHAD_YI notifies you
  3. You re-login manually
  4. Kimi resumes monitoring
Fallback: Manual signal forwarding from you
```

**Scenario 2: CHAD_YI Misses Alert**
```
Detection: No response after 5 minutes
Action:
  1. Kimi resends alert (escalation)
  2. Adds "URGENT" tag
  3. If still no response, notify you directly
Fallback: You step in manually
```

**Scenario 3: Network Partition**
```
Detection: HTTP requests timeout
Action:
  1. Switch to Telegram messaging
  2. If Telegram fails, use file system
  3. If all fail, alert you
Fallback: Manual coordination
```

**Scenario 4: OANDA API Down**
```
Detection: CHAD_YI gets API error
Action:
  1. Log error
  2. Notify you
  3. Queue trade for retry
  4. Retry every 30 seconds (max 5 times)
Fallback: Manual trade execution
```

### 4.2 Escalation Ladder

```
Level 1: Agent handles autonomously
Level 2: Other agent helps
Level 3: Notify you via Telegram
Level 4: Wait for your response
Level 5: Emergency manual mode
```

---

## PHASE 5: ONBOARDING SEQUENCE

### 5.1 Day 1: Setup

**Morning (You):**
```
□ Create Kimi Claw instance
□ Install skills
□ Copy config files
□ Test Telegram
```

**Afternoon (CHAD_YI + Kimi):**
```
□ Establish communication
□ Test message passing
□ Verify file access
□ Run first health check
```

**Evening (Together):**
```
□ Review first reports
□ Fix any issues
□ Confirm working
```

### 5.2 Day 2-3: Testing

**Test Scenarios:**
```
□ Kimi detects dummy signal → CHAD_YI receives
□ CHAD_YI assigns task → Kimi executes
□ Dashboard screenshot → Verified accurate
□ Agent down detection → Alert sent
□ Network failure → Fallback works
```

### 5.3 Day 4-7: Gradual Rollout

**Week 1:**
- Monitor only (no auto-trading)
- CHAD_YI approves each action
- You observe all interactions
- Document issues

**Week 2:**
- Auto-execute low-risk tasks
- CHAD_YI still approves trades
- Reduce manual oversight

**Week 3+:**
- Full autonomy
- You only receive reports
- Intervene only when needed

---

## PHASE 6: DAILY OPERATIONS

### 6.1 Morning Routine (08:00 SGT)

**Kimi-Claw-Helios:**
```
1. Screenshot dashboard
2. Verify all systems green
3. Check overnight signals
4. Send morning report to CHAD_YI
```

**CHAD_YI:**
```
1. Receive Kimi report
2. Review overnight activity
3. Update priorities
4. Send daily briefing to you
```

### 6.2 Continuous Operations

**Every 2 minutes:**
- Kimi checks CallistoFX

**Every 15 minutes:**
- Kimi audits dashboard
- Kimi verifies agent health

**Every hour:**
- CHAD_YI reviews status
- Updates if needed

### 6.3 Evening Routine (23:00 SGT)

**Kimi:**
```
1. Generate daily summary
2. Count signals detected
3. List alerts sent
4. Report to CHAD_YI
```

**CHAD_YI:**
```
1. Compile daily report
2. Update memory files
3. Set priorities for tomorrow
4. Send summary to you
```

---

## PHASE 7: OPTIMIZATIONS (Beyond Current Helios)

### 7.1 What Helios Did Wrong (Fix These)

| Issue | Old Helios | New Kimi-Claw-Helios |
|-------|------------|---------------------|
| Data freshness | Read file only | Screenshot + read |
| Agent checking | ps command | Process + logs + heartbeats |
| Alert spam | Sent everything | Priority-based filtering |
| No browser | Couldn't access web | Full browser automation |
| No memory | Same mistakes | Learns from CHAD_YI |
| Static config | Manual updates | Dynamic from CHAD_YI |

### 7.2 New Capabilities

**Intelligent Alerting:**
```
Don't alert on:
- Dashboard 2 min stale (normal)
- Agent idle < 1 hour (normal)
- Minor stat discrepancies

Do alert on:
- Dashboard > 10 min stale
- Agent down > 1 hour
- Critical deadlines < 8h
- Trading signals (immediate)
```

**Predictive Monitoring:**
```
- Learn patterns from data
- Predict when agents might fail
- Pre-emptive alerts
- Trend analysis
```

**Self-Healing:**
```
- Auto-restart crashed agents
- Reconnect to Telegram if disconnected
- Clear cache if memory full
- Log rotation
```

---

## PHASE 8: SUCCESS METRICS

### 8.1 System Health KPIs

```
Dashboard Accuracy: 99%+ (timestamp < 5 min old)
Signal Detection: < 5 second latency
Trade Execution: < 10 second latency
Uptime: 99.5%+ (Kimi), 95%+ (CHAD_YI)
False Alerts: < 5% of total alerts
Missed Events: 0 (critical events)
```

### 8.2 User Experience KPIs

```
Your Manual Interventions: < 2 per day
Time to Setup: < 1 hour
Time to Recover from Failure: < 5 minutes
Trust Level: High (you can ignore system)
```

---

## APPENDICES

### Appendix A: File Structure

```
~/.openclaw/workspace/
├── MEMORY.md
├── AGENTS.md
├── KIMI_CLAW_HELIOS_CONFIG.md
├── INTEGRATION_GUIDE.md
├── skills/
│   └── kimi-claw-helios/
│       ├── SKILL.md
│       ├── HEARTBEAT.md
│       ├── TELEGRAM_CONFIG.md
│       └── telegram_monitor.py
├── shared/
│   ├── incoming/     # CHAD_YI → Kimi
│   ├── outgoing/     # Kimi → CHAD_YI
│   └── signals/      # Screenshots, etc.
└── memory/
    ├── 2026-02-16.md
    └── ...
```

### Appendix B: Telegram Message Templates

**Signal Detection:**
```
🚨 SIGNAL | {SYMBOL} {DIRECTION}

Entry: {ENTRY}
SL: {SL}
TP: {TPS}

Time: {TIMESTAMP}
Screenshot: {ATTACHED}

CHAD_YI: Execute?
```

**Dashboard Alert:**
```
⚠️ DASHBOARD | {STATUS}

Issue: {DESCRIPTION}
Last Updated: {TIME}
Action Needed: {ACTION}

CHAD_YI: Check?
```

**Task Complete:**
```
✅ TASK | {TASK_ID}

Status: COMPLETE
Result: {SUMMARY}
Time: {DURATION}

CHAD_YI: Updated dashboard.
```

### Appendix C: Quick Reference

**Start Kimi Monitoring:**
```bash
# In Kimi Claw
python3 telegram_monitor.py --continuous
```

**Test Communication:**
```bash
# CHAD_YI sends test
message.send(to="kimi-bridge", text="Test message")

# Kimi responds
telegram.send(to="512366713", text="Received")
```

**Emergency Stop:**
```bash
# Kill all Kimi processes
pkill -f kimi-claw

# Alert you
message.send(to="512366713", text="🛑 SYSTEM PAUSED")
```

---

## CHECKLIST: BEFORE YOU CONNECT

**For You:**
- [ ] Read this entire document
- [ ] Create Kimi Claw instance
- [ ] Install all required skills
- [ ] Configure Telegram bot
- [ ] Test file system access
- [ ] Choose communication method

**For Kimi:**
- [ ] Copy all config files
- [ ] Verify skills installed
- [ ] Test Telegram messaging
- [ ] Confirm workspace access

**For CHAD_YI:**
- [ ] Read this plan
- [ ] Prepare to receive Kimi
- [ ] Test communication channel
- [ ] Update error handling

**Integration Test:**
- [ ] Send test message Kimi → CHAD_YI
- [ ] Send test message CHAD_YI → Kimi
- [ ] Execute test task
- [ ] Verify results

---

## FINAL NOTES

**This is a living document.** Update it as you learn.

**Start small.** Don't enable everything at once.

**Trust takes time.** Begin with monitoring, add automation gradually.

**You are the boss.** Both agents report to you. Override anytime.

**Questions?** Ask before proceeding.

---

**Ready to begin Phase 1?**