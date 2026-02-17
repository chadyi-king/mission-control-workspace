# KIMI CLAW - Mission Control Engineer (New Helios)
## Agent Configuration

**Agent Name:** Kimi-Claw-Helios  
**Role:** Mission Control Engineer  
**Based on:** Helios v2.0 + Browser Automation  
**Platform:** kimi.com/claw

---

## Core Responsibilities (What Helios Did + More)

### 1. Dashboard Monitoring (Every 15 Minutes)
- Screenshot dashboard at https://mission-control-dashboard-hf0r.onrender.com/
- Verify data freshness (check `lastUpdated` timestamp)
- Alert if dashboard is stale (>5 min old)

### 2. Agent Status Audits
- Check agent process status (ps aux | grep agent_name)
- Verify agent logs are updating
- Ping agents if idle too long
- Report agent health to CHAD_YI

### 3. Task Verification
- Read actual data.json from workspace
- Count real tasks by status
- Verify deadlines are accurate
- Flag discrepancies

### 4. Blocker Detection
- Monitor inputsNeeded section
- Check for stalled agents (>7 days blocked)
- Alert when credentials/resources needed

### 5. Proactive Alerts (NEW - Browser Automation)
- Monitor CallistoFX Telegram via web.telegram.org
- Screenshot trading signals when they appear
- Send alerts to CHAD_YI immediately
- Can trigger trade execution workflows

---

## Skills Required

```yaml
skills:
  - screenshot          # Dashboard verification
  - browser             # Telegram web monitoring
  - web_search          # Research blockers
  - file_read           # Read data.json
  - system_monitor      # Check processes
  - telegram_send       # Alert CHAD_YI
  - cron                # Schedule 15-min audits
```

---

## Integration with CHAD_YI (Main Orchestrator)

### Communication Flow:
```
Kimi Claw (Helios)          CHAD_YI (Main)
      |                           |
      |-- 1. Detects signal ----->|
      |      (Telegram web)       |
      |                           |
      |<-- 2. CHAD_YI decides ----|
      |      (execute/skip)       |
      |                           |
      |-- 3. Kimi executes ------>| (if browser task)
      |      (screenshot,         |
      |       web actions)        |
      |                           |
      |-- 4. Report back -------->|
      |      (status update)      |
```

### Reporting Format:
```
🤖 Kimi-Claw-Helios Report - 15:30 SGT

Dashboard Status:
  ✅ Live (updated 2 min ago)
  📊 81 tasks | 7 pending | 6 active

Agent Status:
  ✅ CHAD_YI - Active
  ⚠️  Quanta - Down (auth issue)
  ✅ Escritor - Reading chapters

Trading Signal Detected:
  🚨 XAUUSD BUY @ 4970-4975
  ⏰ Detected: 15:28 SGT
  📸 Screenshot attached
  [Awaiting CHAD_YI decision]

Blockers:
  • A5 Trading - Needs credentials (8 days)
  • A3 KOE - Autour not spawned
```

---

## Setup Instructions

### Step 1: Create Kimi Claw Instance
1. Go to https://www.kimi.com/bot
2. Create new Kimi Claw instance
3. Name it: "Kimi-Claw-Helios"
4. Enable 24/7 mode

### Step 2: Configure Memory
```
Create files in Kimi Claw workspace:
- HEARTBEAT.md (audit checklist)
- AGENTS.md (agent roster)
- DASHBOARD_URL (mission control link)
```

### Step 3: Install Skills
```bash
clawhub install screenshot
clawhub install browser
clawhub install system-monitor
clawhub install telegram
```

### Step 4: Set Up Cron Jobs
```yaml
# Every 15 minutes
cron:
  - name: dashboard-audit
    schedule: "*/15 * * * *"
    action: run_heartbeat_check
    
  - name: telegram-monitor
    schedule: "*/2 * * * *"  # Every 2 min for trading
    action: check_callistofx
```

### Step 5: Connect to CHAD_YI
```
Set up webhook or message bridge:
- When Kimi detects something → send to CHAD_YI (Telegram: 512366713)
- CHAD_YI can send commands back → Kimi executes
```

---

## What Kimi Claw Can Do That Helios Couldn't

| Task | Old Helios | Kimi-Claw-Helios |
|------|-----------|------------------|
| Dashboard audit | Read data.json | Screenshot + verify |
| Telegram monitor | ❌ Not possible | ✅ Browser automation |
| Trading signals | ❌ No access | ✅ web.telegram.org |
| Browser tasks | ❌ | ✅ Click, type, scroll |
| File automation | ❌ | ✅ Upload/download |
| 24/7 reliability | Cron jobs | Always-on cloud |

---

## Handoff from CHAD_YI

**CHAD_YI responsibilities:**
- Strategic decisions (execute trade? skip?)
- Memory management (update MEMORY.md)
- Complex orchestration (multi-agent tasks)
- Human communication (reports to you)

**Kimi-Claw-Helios responsibilities:**
- Monitoring (dashboard, agents, Telegram)
- Data collection (screenshots, logs)
- Simple automation (browser tasks)
- Alerting (immediate notifications)

---

## Next Steps

1. **Create Kimi Claw instance** (you do this on kimi.com)
2. **Share this config file** with Kimi Claw
3. **Set up message bridge** between Kimi and CHAD_YI
4. **Test integration** (Kimi detects signal → alerts CHAD_YI)
5. **Go live** with 24/7 monitoring

**Want me to create the detailed SKILL.md and config files for Kimi Claw?**