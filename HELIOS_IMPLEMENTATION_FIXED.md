# HELIOS_IMPLEMENTATION_FIXED.md
## Fixed Infrastructure with All Gaps Addressed

---

## GAP FIXES

### GAP 1: Helios → CHAD_YI Communication

**Problem:** Helios needs my session key to send messages

**Solution: Message Bus File System**

Helios writes to file → I read file → I respond

```
/agents/message-bus/helios-to-chad-yi/
├── pending/          # Helios writes alerts here
├── acknowledged/     # I move files here after reading
└── resolved/         # After I fix and Helios verifies
```

**Implementation:**
```python
# Helios writes:
write(
  path="/agents/message-bus/helios-to-chad-yi/pending/alert-{timestamp}.md",
  content="ALERT: Quanta status mismatch..."
)

# I (CHAD_YI) poll this directory every few minutes
# When I see new file, I read it and act
# Then move to acknowledged/
```

**Alternative: Direct sessions_send**
```python
# Helios config includes my session key:
chad_yi_session = "agent:main:main"  # My main session

# Helios sends:
sessions_send(
  session_key="agent:main:main",
  message="Helios alert: [specific issue]"
)
```

**Decision:** Use sessions_send (direct) for immediate alerts, file-based for batch reports.

---

### GAP 2: Self-Scheduling (The while loop)

**Problem:** How does Helios run every 15 minutes continuously?

**Solution: Explicit implementation**

```python
# Helios main loop
def run_helios():
    while True:
        try:
            # 1. Run audit cycle
            audit_result = run_15_min_audit()
            
            # 2. Check for immediate alerts
            if audit_result.has_critical:
                send_immediate_alert(audit_result)
            
            # 3. Compile report
            report = compile_report(audit_result)
            
            # 4. Send to CHAD_YI
            send_to_chad_yi(report)
            
            # 5. Sleep 15 minutes
            time.sleep(900)  # 15 minutes = 900 seconds
            
        except Exception as e:
            log_error(e)
            time.sleep(60)  # Retry in 1 min on error

# Start Helios
run_helios()
```

**Handling runTimeoutSeconds:**
- Current spawn: `runTimeoutSeconds=600` (10 min)
- Problem: Helios dies after 10 min
- Solution: Spawn with `runTimeoutSeconds=0` (no timeout) if allowed, OR use cron to respawn

**Decision:** Request `runTimeoutSeconds=0` for Helios (continuous operation).

---

### GAP 3: Quanta is NOT Running

**Problem:** No active Quanta session found

**Solution: Spawn Quanta as Persistent Session**

**Quanta's Role:**
- Monitor CallistoFX Telegram channel continuously
- Capture signals immediately
- Alert Helios immediately (not just write to file)
- Report status to Helios when pinged

**Implementation:**
```python
# Spawn Quanta as persistent session
sessions_spawn(
    agent_id="quanta",
    label="Quanta Trading Agent - Persistent",
    runTimeoutSeconds=0,  # No timeout, runs continuously
    task="""
    You are Quanta, the Trading Dev.
    
    Your job:
    1. Monitor CallistoFX Telegram channel continuously
    2. Capture trading signals immediately
    3. Write signals to /agents/quanta/signals/PENDING/
    4. ALERT HELIOS IMMEDIATELY via sessions_send when signal captured
    5. Respond to Helios status pings
    
    Alert format to Helios:
    sessions_send to=helios:
    "NEW SIGNAL: XAUUSD BUY 2680-2685, SL 2675, TPs 2700/2720/2740"
    
    Status response format:
    "Quanta: Monitoring XAUUSD, last signal at 09:15, no entry yet"
    
    Run continuously. Check Telegram every 30 seconds.
    """
)
```

**Decision:** Spawn Quanta as persistent session FIRST, then deploy Helios.

---

### GAP 4: "Real-Time" Clarification

**Problem:** Plan says "real-time" but file-based = 15-min delay

**Honest Assessment:**

| Agent Type | Response Time | Method |
|------------|---------------|--------|
| Quanta (persistent) | Immediate | sessions_send |
| Escritor (file-based) | 15-min delay | File read |
| MensaMusa (not spawned) | N/A | N/A |

**Revised Promise:**
- **Immediate (0-30 sec):** Quanta signals, critical alerts
- **Near real-time (15 min):** File-based agent updates, dashboard verification
- **Batch (daily):** Digest reports

---

### GAP 5: Session Timeout Handling

**Problem:** Helios dies after runTimeoutSeconds

**Solutions:**

**Option A: No Timeout (Preferred)**
```python
sessions_spawn(
    runTimeoutSeconds=0,  # Run indefinitely
    task="..."
)
```

**Option B: Cron Respawn (Fallback)**
```python
# Cron job every 15 min:
# Check if Helios session exists
# If not, spawn new Helios session
```

**Option C: Heartbeat Ping (Current)**
```python
# Helios sends heartbeat to himself every 10 min
# If no heartbeat, spawn new instance
```

**Decision:** Request Option A (no timeout) for Helios.

---

### GAP 6: Non-Response Escalation

**Problem:** What if I don't respond to Helios alerts?

**Escalation Protocol:**

```
T+0: Helios sends alert to CHAD_YI
T+15 min: Helios checks if acknowledged (did I move file to acknowledged/?)
T+30 min: If not acknowledged, Helios resends with "URGENT - 2nd notice"
T+1 hour: If not acknowledged, Helios escalates to Caleb directly

Escalation message to Caleb:
"Helios → Caleb: CHAD_YI has not responded to critical alert for 1 hour.
Issue: [description]
Action needed: [specific action]"
```

**Implementation:**
```python
def check_acknowledgment(alert_id):
    acknowledged_file = f"/agents/message-bus/helios-to-chad-yi/acknowledged/{alert_id}.md"
    return file_exists(acknowledged_file)

def handle_non_response(alert):
    if not check_acknowledgment(alert.id):
        if alert.age > 3600:  # 1 hour
            escalate_to_caleb(alert)
        elif alert.age > 1800:  # 30 min
            resend_as_urgent(alert)
```

---

## REVISED DEPLOYMENT PLAN

### Phase 1: Fix Infrastructure (Today)

**Step 1: Update Message Bus**
- Create `/agents/message-bus/helios-to-chad-yi/` structure
- Create `/agents/message-bus/chad-yi-to-helios/` for my responses
- Create acknowledgment protocol

**Step 2: Fix Helios Config**
- Add my session key: `chad_yi_session = "agent:main:main"`
- Set `runTimeoutSeconds=0` (continuous)
- Add while loop with 15-min sleep
- Add escalation protocol

**Step 3: Document Honest Limitations**
- Quanta = immediate (when persistent)
- Escritor = 15-min delay (file-based)
- Dashboard = 15-min verification cycle

### Phase 2: Spawn Agents (Today)

**Step 1: Spawn Quanta (Persistent)**
```python
sessions_spawn(
    label="Quanta Trading - Persistent",
    runTimeoutSeconds=0,
    task="Monitor CallistoFX, capture signals, alert Helios immediately"
)
```

**Step 2: Spawn Helios (Fixed)**
```python
sessions_spawn(
    label="Helios Coordinator - Fixed",
    runTimeoutSeconds=0,
    task="15-min audit cycle, immediate alerts, escalation protocol"
)
```

**Step 3: Verify Communication**
- Helios pings Quanta → Quanta responds
- Helios detects signal → Alerts me immediately
- I fix dashboard → Helios verifies

### Phase 3: Testing (Today)

**Test 1: File Monitoring**
- Escritor updates current-task.md
- Helios detects in next cycle (within 15 min)
- Helios reports to me

**Test 2: Immediate Alert**
- Quanta captures signal
- Quanta alerts Helios immediately
- Helios alerts me immediately (within 30 sec)

**Test 3: Dashboard Verification**
- I deliberately break dashboard (wrong status)
- Helios detects discrepancy
- Helios sends specific fix instructions
- I fix it
- Helios verifies

**Test 4: Escalation**
- Helios sends alert
- I don't respond for 1 hour
- Helios escalates to Caleb

---

## REVISED SUCCESS CRITERIA

**Immediate (0-30 sec):**
- ✅ Quanta signals captured and reported
- ✅ Critical alerts sent to me

**Near Real-Time (15 min):**
- ✅ File-based agent updates detected
- ✅ Dashboard discrepancies found
- ✅ Status reports compiled

**Reliable (100%):**
- ✅ No missed critical deadlines
- ✅ Dashboard accuracy >95%
- ✅ Escalation works if I'm unresponsive

---

## FILES TO UPDATE

1. `/agents/helios/AGENT_STATE.json` - Add session keys, timeout=0
2. `/agents/helios/SOUL.md` - Add escalation protocol, honest timing
3. Create `/agents/message-bus/` structure
4. `/HELIOS_INFRASTRUCTURE_PLAN.md` - Update with fixes
5. `/CHAD_YI_AND_HELIOS_ROLES.md` - Update with honest limitations

---

## DEPLOYMENT READY CHECKLIST

- [ ] Message bus structure created
- [ ] Helios config updated (session keys, timeout=0)
- [ ] Escalation protocol defined
- [ ] Quanta spawn script ready
- [ ] Helios spawn script ready (with while loop)
- [ ] Testing protocol defined
- [ ] Honest limitations documented

---

**Status:** Gaps identified and fixed. Ready for deployment once you approve.
