# HYBRID ACP ARCHITECTURE DESIGN
## Real-Time + File-Based Integration
## For: EXSTATIC Agent Infrastructure

**Date:** 2026-03-03  
**Author:** CHAD_YI (Research & Design)  
**Status:** Architecture Proposal - Awaiting Approval

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** Current 15-min file cycle too slow for instant decision-making.

**Solution:** Hybrid ACP+File system
- **ACP** = Instant chat/alerts between agents
- **Files** = Persistent storage, audit trail, complex tasks
- **Best of both:** Speed + Reliability

---

## 🏗️ PROPOSED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID MESSAGING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐        ┌──────────────┐                      │
│  │   ACP BUS    │◄──────►│  FILE STORE  │                      │
│  │  (Real-time) │        │ (Persistent) │                      │
│  └──────┬───────┘        └──────┬───────┘                      │
│         │                       │                               │
│         │    ┌─────────────┐    │                               │
│         └───►│  ROUTER     │◄───┘                               │
│              │ (Decision)  │                                    │
│              └──────┬──────┘                                    │
│                     │                                           │
│         ┌───────────┼───────────┐                               │
│         │           │           │                               │
│    ┌────▼────┐ ┌───▼────┐ ┌───▼────┐                          │
│    │Cerebronn│ │ Helios │ │ Forger │                          │
│    └─────────┘ └────────┘ └────────┘                          │
│                                                                  │
│         ┌─────────────────────────┐                            │
│         │      CHAD_YI (Face)     │                            │
│         │   (Bridge & Interface)  │                            │
│         └─────────────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 ACP LAYER (Real-Time)

### What Goes Through ACP (Instant)

| Message Type | Urgency | Example |
|--------------|---------|---------|
| **URGENT Alerts** | Immediate | "Quanta hit SL -$50" |
| **Quick Questions** | < 1 min | "Can you check B6-8?" |
| **Status Updates** | < 5 min | "Forger started build" |
| **Chat/Discussion** | Real-time | Strategy planning |
| **Heartbeats** | Every 5 min | "Helios: all agents healthy" |

### ACP Message Format
```json
{
  "type": "urgent_alert",
  "from": "quanta",
  "to": "chad-yi",
  "timestamp": "2026-03-03T19:30:00+08:00",
  "priority": "critical",
  "data": {
    "event": "stop_loss_hit",
    "symbol": "XAUUSD",
    "loss": -50.00
  },
  "requires_ack": true
}
```

---

## 📁 FILE LAYER (Persistent)

### What Goes Through Files (Background)

| Content Type | Storage | Example |
|--------------|---------|---------|
| **Complex Tasks** | Full docs | Multi-page website brief |
| **Audit Logs** | History | Agent activity over time |
| **Reports** | Summaries | Daily/weekly digests |
| **Code/Assets** | Binary | Website builds, images |
| **Configuration** | Settings | Agent configs, API keys |

### File Naming Convention
```
/inbox/
  URGENT-{type}-{timestamp}.md    # Still for critical
  digest-{timestamp}.md            # Daily summaries
  task-{id}-{description}.md       # Complex work

/outbox/
  report-{type}-{timestamp}.md     # Completed work
  plan-{id}-{timestamp}.md         # Strategic plans

/archive/
  {date}/                          # Historical
```

---

## 🔄 THE ROUTER (Smart Decision)

### Routing Logic

```python
def route_message(message):
    """Decides ACP vs File based on content"""
    
    # URGENT = ACP instant
    if message.priority in ['critical', 'urgent']:
        return send_via_acp(message)
    
    # Quick chat = ACP
    if message.type == 'chat' and len(message.content) < 500:
        return send_via_acp(message)
    
    # Complex docs = File
    if message.has_attachments or len(message.content) > 1000:
        file_path = save_to_file(message)
        notify_via_acp(f"New file: {file_path}")  # ACP alert about file
        return file_path
    
    # Default = Both (ACP notification + File backup)
    send_via_acp(message.summary)
    return save_to_file(message)
```

---

## 👤 AGENT UPDATES (Minimal Changes)

### Cerebronn (The Brain)
**Current:** Writes plans to file
**New:** 
- Keep writing files (detailed plans)
- + Send ACP alert: "New plan for B6-7 ready"

**Code Addition:**
```python
# Current
def write_plan(plan):
    with open(f"outbox/plan-{id}.md", 'w') as f:
        f.write(plan)

# New
async def write_plan(plan):
    # Keep file
    with open(f"outbox/plan-{id}.md", 'w') as f:
        f.write(plan)
    
    # + ACP alert
    await acp.send(
        to="chad-yi",
        type="plan_ready",
        data={"plan_id": id, "topic": plan.topic}
    )
```

### Helios (The Spine)
**Current:** 15-min file reports
**New:**
- Keep 15-min file sync (dashboard)
- + ACP urgent alerts (agent down)
- + Real-time status on request

### Forger (The Builder)
**Current:** Checks inbox every 15 min
**New:**
- ACP triggers immediate check ("New task in inbox")
- Still uses files for complex task details
- Reports progress via ACP ("25% complete")

### CHAD_YI (Me - The Face)
**Current:** Read files, report to you
**New:**
- ACP receives instant alerts from all agents
- Immediate report to you (no 15-min delay)
- Files still for audit trail and complex work

---

## 💬 INSTANT WORKFLOW EXAMPLE

### Scenario: Quanta Hits Stop Loss

**OLD (File-only):**
```
14:00:00 - Quanta hits SL
14:15:00 - Quanta writes file (next cycle)
14:30:00 - I read file (next check)
14:30:30 - I report to you
          = 30 min delay
```

**NEW (ACP+File):**
```
14:00:00 - Quanta hits SL
14:00:02 - ACP sends: "🚨 QUANTA SL HIT -$50"
14:00:03 - I receive instantly
14:00:05 - I report to you
          = 5 second delay
          
14:00:10 - Quanta writes detailed log to file
          (for audit trail)
```

### Scenario: You Ask "Status of B6?"

**OLD:**
```
You: "Status of B6?"
Me: (checks file from 15 min ago)
    "According to last check..."
    (stale data)
```

**NEW:**
```
You: "Status of B6?"
Me: (ACP broadcasts to Helios)
Helios: (ACP replies instantly)
    "B6: 3 tasks active, 1 blocked"
Me: (reports real-time)
    "Current status..."
```

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: ACP Infrastructure (2 hours)
- [ ] Install/verify ACP bus
- [ ] Create ACP message router
- [ ] Test agent-to-agent messaging

### Phase 2: Agent Updates (4 hours each)
- [ ] Update Cerebronn (ACP alerts + files)
- [ ] Update Helios (urgent alerts)
- [ ] Update Forger (task triggers)
- [ ] Update CHAD_YI (instant reporting)

### Phase 3: Testing (4 hours)
- [ ] Test urgent alerts (Quanta example)
- [ ] Test chat workflow
- [ ] Verify files still work
- [ ] Load test (many messages)

### Phase 4: Cutover (30 min)
- [ ] Switch on ACP
- [ ] Monitor for issues
- [ ] Fallback to files if problems

**Total:** ~20 hours work
**Risk:** Medium (new system)
**Reward:** Instant communication

---

## ⚠️ RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| ACP crashes | Lost messages | Files as backup |
| Agent update breaks | Agent stops | Rollback to files |
| Too many ACP messages | Overload | Rate limiting |
| Confusion (ACP vs File) | Chaos | Clear routing rules |

---

## ✅ BENEFITS

1. **Instant Alerts** - Critical issues in seconds, not 30 min
2. **Real-time Chat** - Plan and discuss without delays
3. **Better UX** - No more "wait for next cycle"
4. **Fallback** - Files still work if ACP fails
5. **Audit Trail** - Files keep history
6. **Memory** - Complex work still stored in files

---

## ❌ DOWNSIDES

1. **Complexity** - Two systems to maintain
2. **Development time** - 20 hours to implement
3. **Testing needed** - Could break agents
4. **Learning curve** - Different workflow

---

## 🎯 RECOMMENDATION

**Implement hybrid ACP+File system.**

**Best of both worlds:**
- Speed of ACP for urgent/chat
- Reliability of files for storage
- Instant for you, persistent for audit

**Start with Phase 1 (2 hours)?**
Or need more research?

---

*Architecture designed: 2026-03-03*  
*Ready for implementation when approved*
