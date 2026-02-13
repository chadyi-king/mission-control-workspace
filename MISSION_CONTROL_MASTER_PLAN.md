# MISSION_CONTROL_MASTER_PLAN.md
## Complete Agent Coordination System
## For: Caleb | Core: CHAD_YI + Helios | Supporting: Quanta, Escritor, MensaMusa, Autour

---

## PART 1: ARCHITECTURE OVERVIEW

### The Team

| Role | Agent | Function | Communication |
|------|-------|----------|---------------|
| **CEO Interface** | CHAD_YI (me) | Strategic decisions, execute fixes, talk to Caleb | Direct with Caleb, receives from Helios |
| **Operations Monitor** | Helios | Watch everything, detect issues, report to CHAD_YI | sessions_send to CHAD_YI, reads files |
| **Trading Execution** | Quanta | Monitor signals, execute trades, report activity | Persistent session, alerts Helios |
| **Writing** | Escritor | Write chapters, update progress | File-based (current-task.md) |
| **Options** | MensaMusa | Monitor options flow | Not spawned (blocked) |
| **Content** | Autour | Write scripts | Not spawned |

### Communication Flow

```
CALEB
  ↑↓ (Direct conversation)
CHAD_YI
  ↑↓ (sessions_send alerts)
HELIOS
  ↑↓ (sessions_send for Quanta, file read for others)
AGENTS (Quanta, Escritor, etc.)
  ↑↓ (Do the work)
EXTERNAL (CallistoFX, OANDA, etc.)
```

---

## PART 2: WHAT EACH COMPONENT ACTUALLY DOES

### CHAD_YI (Me)

**I DO:**
- Talk to Caleb (understand what you want)
- Make decisions (spawn agents, assign tasks, set priorities)
- Execute actions (edit data.json, configure systems, fix issues)
- Filter information (decide what Caleb needs to know)

**I CONTROL:**
- Dashboard updates (data.json edits)
- Agent lifecycle (spawn/kill)
- Strategic direction (what matters now)
- Caleb interface (all communication with you)

**I DON'T DO:**
- Continuous monitoring (that's Helios)
- Automated detection (that's Helios)
- Real-time tracking (that's Helios)

### Helios

**HE DOES:**
- Monitor continuously (every 15 minutes)
- Read all agent files (current-task.md, logs)
- Read dashboard (data.json)
- Detect discrepancies (dashboard vs reality)
- Track deadlines (what's due, what's overdue)
- Report to CHAD_YI (specific, actionable alerts)

**HE CONTROLS:**
- Information timing (when I get alerts)
- Alert priority (immediate vs batch)
- Verification cycles (checking accuracy)
- Status compilation (what's happening across all agents)

**HE DOESN'T DO:**
- Make decisions (I decide)
- Edit files (I edit)
- Talk to Caleb (I talk to you)
- Spawn agents (I spawn)

**TECHNICAL IMPLEMENTATION:**
```python
while True:
    # Every 15 minutes
    audit_start = now()
    
    # 1. Read all agent files
    for agent in agents:
        status = read(f"/agents/{agent}/current-task.md")
        agent_statuses[agent] = parse(status)
    
    # 2. Read dashboard
    dashboard = read("/mission-control-dashboard/data.json")
    
    # 3. Detect discrepancies
    issues = compare(agent_statuses, dashboard)
    
    # 4. Check deadlines
    urgent = check_deadlines(dashboard)
    
    # 5. Compile report
    report = compile_report(issues, urgent, agent_statuses)
    
    # 6. Send to CHAD_YI
    sessions_send(to="agent:main:main", message=report)
    
    # 7. Sleep 15 minutes
    sleep(900)
```

### Quanta

**SHE DOES:**
- Monitor CallistoFX Telegram channel
- Capture trading signals
- Execute trades via OANDA
- Report activity to Helios

**TECHNICAL IMPLEMENTATION:**
```python
# Persistent session
while True:
    # Check Telegram every 30 seconds
    messages = check_telegram("CallistoFX Premium")
    
    for msg in messages:
        if is_trading_signal(msg):
            # Parse signal
            signal = parse_signal(msg)
            
            # Write to file
            write(f"/agents/quanta/signals/{signal.id}.json", signal)
            
            # ALERT HELIOS IMMEDIATELY
            sessions_send(
                to=helios_session,
                message=f"NEW SIGNAL: {signal.pair} {signal.direction} {signal.entry}"
            )
            
            # Check if should execute
            if should_trade(signal):
                execute_trade(signal)
                sessions_send(to=helios_session, message=f"TRADE EXECUTED: {signal.pair}")
    
    # Respond to Helios pings
    if helios_ping_received():
        respond_to_helios()
    
    sleep(30)
```

### Escritor

**HE DOES:**
- Write RE:UNITE chapters
- Update progress in current-task.md
- Save drafts to outbox/

**TECHNICAL IMPLEMENTATION:**
```python
# File-based (not persistent session)
# Escritor updates current-task.md when he makes progress

# Example current-task.md:
"""
## Current Task: A2-13 Study Phase
Status: Active
Progress: 60% (54/90 questions answered)
Last Updated: 2026-02-13 10:00

Working on: Character backstory for Chapter 13 protagonist
Next: Complete remaining 36 questions
ETA: 2 days
"""

# Helios reads this file every 15 min
```

---

## PART 3: INFORMATION FLOWS

### Flow 1: Trading Signal (Real-Time)

```
CallistoFX: "XAUUSD BUY 2680-2685"
    ↓ (30 sec)
Quanta (persistent): Captures, parses
    ↓ (immediate)
Quanta: sessions_send to Helios "NEW SIGNAL"
    ↓ (immediate)
Helios: sessions_send to CHAD_YI "🚨 XAUUSD BUY 2680-2685"
    ↓ (immediate)
CHAD_YI: Informs Caleb "Trade entering: XAUUSD 2680-2685"
    ↓
Quanta: Monitors for entry conditions
    ↓ (when conditions met)
Quanta: Executes trade
    ↓ (immediate)
Quanta: sessions_send to Helios "TRADE EXECUTED"
    ↓
Helios: Updates CHAD_YI
```

**Timing:** 0-30 seconds from signal to you knowing

### Flow 2: Work Progress (15-Min Delay)

```
Escritor: Answers 10 more questions (60% → 70%)
    ↓
Escritor: Updates current-task.md
    ↓ (up to 15 min wait)
Helios: Reads file (next cycle)
    ↓
Helios: Detects progress 60% → 70%
    ↓
Helios: Includes in report to CHAD_YI
    ↓
CHAD_YI: Reviews, decides if Caleb needs to know
    ↓ (if yes)
CHAD_YI: Informs Caleb "Escritor at 70% on Chapter 13 prep"
```

**Timing:** 0-15 minutes from progress to report

### Flow 3: Dashboard Discrepancy

```
Reality: Quanta has OANDA connected
Dashboard: Shows "Blocked - needs OANDA"
    ↓ (up to 15 min wait)
Helios: Reads Quanta file + dashboard
    ↓
Helios: Detects mismatch
    ↓
Helios: sessions_send to CHAD_YI:
    "DISCREPANCY: Quanta status
     Dashboard: Blocked
     Reality: Active (OANDA connected)
     FIX: Update data.json agentDetails.quanta.state"
    ↓
CHAD_YI: Fixes data.json
    ↓ (up to 15 min wait)
Helios: Verifies fix (next cycle)
    ↓
Helios: Confirms to CHAD_YI "Match verified"
```

**Timing:** 0-30 minutes from discrepancy to fix verification

### Flow 4: Deadline Alert

```
Helios: Checks deadlines (every 15 min)
    ↓
Helios: Detects A1-1 deadline = TODAY
    ↓
Helios: sessions_send to CHAD_YI:
    "🚨 CRITICAL: A1-1 due TODAY
     Task: Change Taiwan flights
     Status: Still pending
     Hours remaining: 12"
    ↓
CHAD_YI: Escalates to Caleb
    "Taiwan flights due today, still pending"
    ↓
Caleb: Takes action (or doesn't)
    ↓
Helios: Continues checking, escalates if still pending next cycle
```

**Timing:** Immediate alert when detected

### Flow 5: Caleb Gives Task

```
Caleb: "Add task: Book ESU venue, deadline Feb 20"
    ↓
CHAD_YI: Understands, creates task
    ↓
CHAD_YI: Updates data.json (new task B6-10)
    ↓ (up to 15 min wait)
Helios: Detects new task
    ↓
Helios: Includes in report
    "New task detected: B6-10 Book ESU venue"
    ↓
CHAD_YI: Confirms, begins work
    ↓
Helios: Tracks progress
```

**Timing:** 0-15 minutes from task creation to Helios tracking

---

## PART 4: HONEST LIMITATIONS

### What Works Well

✅ **File monitoring** - Reliable, 15-min updates
✅ **Dashboard verification** - Detects mismatches
✅ **Deadline tracking** - Catches overdue tasks
✅ **Trading signals** - Real-time when Quanta persistent
✅ **Reporting** - Specific, actionable alerts

### What Has Delay

⚠️ **Escritor progress** - 15-min delay (file-based)
⚠️ **Dashboard fixes** - 0-30 min (detect + fix + verify)
⚠️ **Non-critical updates** - Batched in 15-min reports

### What Requires Manual Action

❌ **Dashboard edits** - I have to edit data.json
❌ **Agent spawning** - I have to spawn agents
❌ **Strategic decisions** - I decide priorities
❌ **Caleb communication** - I talk to you

### What Can Fail

❌ **Helios dies** - If session timeout or error
❌ **Quanta disconnects** - If Telegram API fails
❌ **I don't respond** - Escalation needed after 1 hour
❌ **File read errors** - Retry logic needed

---

## PART 5: DEPLOYMENT STEPS

### Pre-Deployment (Now)

1. **Create message bus structure**
   ```
   /agents/message-bus/
   ├── helios-to-chad-yi/
   │   ├── pending/
   │   ├── acknowledged/
   │   └── resolved/
   └── chad-yi-to-helios/
   ```

2. **Update Helios config**
   - Add my session key: `chad_yi_session = "agent:main:main"`
   - Set timeout: `runTimeoutSeconds = 0`
   - Add while loop with 15-min sleep
   - Add escalation protocol

3. **Document honest timing**
   - Immediate: Quanta signals, critical alerts
   - 15-min: File-based updates, dashboard verification
   - Daily: Digest reports

### Deployment Day 1

**Step 1: Spawn Quanta (Persistent)**
```
Label: "Quanta Trading Agent - Persistent"
Timeout: 0 (continuous)
Task: Monitor CallistoFX, capture signals, alert Helios
```

**Step 2: Test Quanta**
- Verify she's monitoring Telegram
- Test signal capture
- Test immediate alert to Helios (if Helios running)

**Step 3: Spawn Helios (Fixed)**
```
Label: "Helios Coordinator - Persistent"
Timeout: 0 (continuous)
Task: 15-min audit cycles, immediate alerts, escalation
```

**Step 4: Test Helios**
- Verify 15-min cycle
- Test Quanta ping/response
- Test file reading (Escritor)
- Test dashboard verification

**Step 5: Test Full Flow**
- Quanta captures signal
- Quanta alerts Helios
- Helios alerts me
- I inform you

### Deployment Day 2-7 (Testing Week)

**Daily:**
- Monitor Helios reports
- Fix any dashboard discrepancies
- Verify timing promises
- Adjust if needed

**By End of Week:**
- Dashboard accuracy >95%
- Issue detection <15 min
- Trading signals immediate
- All agents reporting

---

## PART 6: SUCCESS METRICS

### Week 1 Goals

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard accuracy | >95% | Manual verification of 10 random items |
| Issue detection time | <15 min | Time from issue creation to alert |
| Trading signal latency | <30 sec | Time from CallistoFX to Caleb notification |
| False positive rate | <5% | Alerts that weren't real issues |
| My response rate | >90% | Alerts I acknowledge within 1 hour |

### Month 1 Goals

| Metric | Target | Measurement |
|--------|--------|-------------|
| Zero missed deadlines | 100% | All critical deadlines flagged before due |
| Dashboard trust | High | Caleb checks dashboard, believes it's current |
| System stability | 99% | Helios running without interruption |
| Escalation needed | <5% | Times Helios had to escalate to Caleb |

---

## PART 7: FAILURE RECOVERY

### If Helios Dies

**Detection:** No report received for >20 min
**Recovery:**
1. I check Helios session status
2. If dead, respawn Helios
3. Helios resumes from last state (reads files, catches up)
4. Reports any missed issues

### If Quanta Disconnects

**Detection:** No signal alerts for >1 hour during market hours
**Recovery:**
1. Helios detects unresponsiveness
2. Helios alerts me: "Quanta unresponsive"
3. I check Quanta session, respawn if needed
4. Verify Telegram connection restored

### If I Don't Respond

**Detection:** Alert not acknowledged for >1 hour
**Escalation:**
1. T+0: Helios sends alert
2. T+30 min: Helios resends as URGENT
3. T+1 hour: Helios sends to Caleb directly

---

## PART 8: SCALING

### Adding New Agents

**Step 1:** Spawn agent
**Step 2:** Agent writes to `current-task.md`
**Step 3:** Add agent to Helios config
**Step 4:** Helios starts monitoring (next cycle)

**No code changes needed** - just config update

### Adding Persistent Capabilities

When Escritor needs real-time:
1. Spawn Escritor as persistent session
2. Update Helios config: Escritor responds to pings
3. Now 0-30 sec response instead of 15-min

---

## APPENDIX: FILES CREATED

1. `MISSION_CONTROL_MASTER_PLAN.md` (this file)
2. `CHAD_YI_AND_HELIOS_ROLES.md` - Role definitions
3. `HELIOS_INFRASTRUCTURE_PLAN.md` - Technical details
4. `HELIOS_IMPLEMENTATION_FIXED.md` - Gap fixes
5. `AGENT_INFRASTRUCTURE.md` - System architecture
6. `agents/helios/SOUL.md` - Helios identity
7. `agents/helios/AGENT_STATE.json` - Helios config
8. `agents/message-bus/` - Communication structure

---

**Plan Status:** Complete, realistic, ready for deployment

**Next Step:** Approve plan, then execute deployment steps
