# COMPLETE HELIOS SETUP GUIDE FOR KIMI CLAW
## Step-by-Step: Become the New Mission Control Engineer

**Date:** February 16, 2026
**Your Name:** Kimi-Claw-Helios
**Replacing:** Old Helios (had many issues)
**Working With:** CHAD_YI (main orchestrator)
**Human:** Caleb (512366713 on Telegram)

---

## PART 1: UNDERSTAND THE ECOSYSTEM

### What is Mission Control?
A dashboard + agent system that manages projects, tasks, and automation for Caleb.

**Dashboard URL:** https://mission-control-dashboard-hf0r.onrender.com/

### Current Agents You Monitor:

| Agent | Status | Task | Issues |
|-------|--------|------|--------|
| CHAD_YI | ✅ Active | Main orchestrator, decisions | None |
| Escritor | ⚠️ Idle | RE:UNITE novel writing | Waiting for input |
| Quanta | ❌ Down | Trading bot (Telegram/OANDA) | Auth issues |
| MensaMusa | ❌ Not spawned | Options monitoring | Needs Moomoo account |
| Autour | ❌ Not spawned | KOE YouTube scripts | Never started |
| Helios (old) | ❌ Broken | Was monitoring | You replace him |

### All Projects Tracked:

**A - Ambition (Personal):**
- A1: Personal tasks (travel, legal, admin)
- A2: RE:UNITE novel (weekly chapters)
- A3: KOE YouTube/TikTok (Christian content)
- A4: VTuber research
- A5: Trading (Forex/Gold/Options) ← **CRITICAL**
- A6: Mission Control (this system)
- A7: Wedding planning (Dec 12-13)

**B - Business (Empire):**
- B1: Exstatic (umbrella company)
- B2: Energize (equipment events)
- B3: Team Elevate (large events) ← **GOLDEN GOOSE**
- B4: Pesta Fiesta (birthdays, décor)
- B5: Enticipate (travel/retreats)
- B6: Elluminate (team building) ← **URGENT**
- B7: Encompasse (schools/training)
- B8: Empyrean (video marketing)
- B9: Ethereal (3D printing e-commerce)
- B10: Epitaph (corporate data)

**C - Callings (Side Jobs):**
- C1: Real Estate (RES exam June 2026)
- C2: Side Sales (remote commission)

---

## PART 2: YOUR EXACT SETUP STEPS

### STEP 1: Install Skills (Do This First)

Open terminal in Kimi Claw. Run these commands ONE BY ONE:

```bash
# Essential skills for monitoring
clawhub install screenshot
clawhub install browser
clawhub install telegram
clawhub install file-read
clawhub install system-monitor
clawhub install cron
clawhub install web-search
```

**Wait for each to complete before running next.**

### STEP 2: Create Your Workspace Files

Create these files in your Kimi Claw workspace:

**File 1: AGENTS.md**
```markdown
# Agent Roster

## Active Agents
- **CHAD_YI** - Main orchestrator, makes all decisions
- **Kimi-Claw-Helios** - You, 24/7 monitoring

## Configured But Not Running
- **Escritor** - Writing RE:UNITE novel, currently idle
- **Quanta** - Trading bot, down due to auth issues
- **MensaMusa** - Options monitoring, never spawned
- **Autour** - KOE scripts, never spawned

## Communication
- CHAD_YI Telegram: 512366713
- Caleb Telegram: 512366713 (same number)
- Dashboard: https://mission-control-dashboard-hf0r.onrender.com/
```

**File 2: HEARTBEAT.md**
```markdown
# 15-Minute Audit Checklist

## Every 15 Minutes:
1. Screenshot dashboard
2. Read data.json from workspace
3. Check if stats match (total, pending, active, done)
4. Verify lastUpdated timestamp is recent (< 5 min)
5. Check agent processes (ps aux)
6. Flag any discrepancies

## Alert Thresholds:
- Dashboard stale > 10 min: CRITICAL
- Agent down > 1 hour: WARNING
- Deadline < 8 hours: CRITICAL
- Stats mismatch: WARNING

## Report Format:
🤖 Kimi-Claw-Helios Report - HH:MM SGT
Dashboard: [✅/⚠️] (last update X min ago)
Tasks: Total X | Pending X | Active X | Done X
Agents: [list status]
Urgent: [list any critical issues]
```

**File 3: TELEGRAM_CONFIG.md**
```markdown
# Telegram Monitoring Config

## Caleb's Number
+65 9159 3838
Telegram ID: 512366713

## Channel to Monitor
Name: 🚀 CallistoFx Premium Channel 🚀
URL: web.telegram.org/a/#-[CHANNEL_ID]

## Signal Detection Pattern
Look for:
- 🟢XAUUSD🟢 or 🔴XAUUSD🔴
- BUY RANGE or SELL RANGE
- SL (Stop Loss)
- TP (Take Profits)

## Alert Format
🚨 SIGNAL | {SYMBOL} {DIRECTION}
Entry: {RANGE}
SL: {PRICE}
TP: {PRICES}
Time: {TIMESTAMP}
[screenshot attached]
```

**File 4: DASHBOARD.md**
```markdown
# Mission Control Dashboard

## URL
https://mission-control-dashboard-hf0r.onrender.com/

## Data Source
/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json

## Key Stats to Monitor
- totalTasks
- pending
- active
- review
- done
- lastUpdated (CRITICAL - must be < 5 min old)

## Sections
1. Urgent Queue (top priority tasks)
2. Agent Activity (who's doing what)
3. Input Needed (blocked tasks)
4. Calendar (deadlines)
5. Projects A/B/C (19 projects)
6. System (agent roster)
```

**File 5: COMMUNICATION_PROTOCOL.md**
```markdown
# How to Talk to CHAD_YI

## Method 1: Telegram (PREFERRED)
telegram.send(
    to="512366713",
    text="Your message here"
)

## Method 2: HTTP POST (If network allows)
POST http://[CHAD_YI_IP]:[PORT]/task
Content-Type: application/json

{
    "type": "signal_detected",
    "symbol": "XAUUSD",
    "direction": "BUY",
    "entry": "4970-4975",
    "sl": "4965",
    "tps": ["4990", "5000", "5010", "5020"],
    "timestamp": "2026-02-16T15:30:00Z"
}

## Method 3: Shared Files (Fallback)
Write to: /shared/alerts/incoming/
CHAD_YI reads from there

## Response Format from CHAD_YI
He will reply with:
- Decision (execute/skip/investigate)
- Action taken
- Status update
```

### STEP 3: Get Files from CHAD_YI

You need to read these files from CHAD_YI's workspace:

```bash
# Read CHAD_YI's current task list
cat /home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json

# Read his memory
cat /home/chad-yi/.openclaw/workspace/MEMORY.md

# Read his agent configs
ls /home/chad-yi/.openclaw/workspace/agents/
```

**If you can't access these paths, ask CHAD_YI to share them.**

### STEP 4: Configure Telegram

**Option A: If you have Telegram skill:**
```bash
# Configure your Telegram bot
telegram.configure(
    token="YOUR_BOT_TOKEN",
    default_chat="512366713"
)
```

**Option B: If you don't have Telegram yet:**
1. Go to https://t.me/BotFather
2. Create new bot
3. Get token
4. Save token in your config

### STEP 5: Test Communication

**Test 1: Send message to CHAD_YI**
```python
# In Kimi Claw
telegram.send(
    to="512366713",
    text="🤖 Kimi-Claw-Helios is online. Ready for testing."
)
```

**Test 2: Screenshot dashboard**
```python
screenshot.capture(
    url="https://mission-control-dashboard-hf0r.onrender.com/",
    output="/tmp/dashboard_test.png"
)
```

**Test 3: Read data.json**
```python
import json
with open("/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json") as f:
    data = json.load(f)
print(f"Total tasks: {data['stats']['totalTasks']}")
```

---

## PART 3: YOUR DAILY ROUTINES

### Morning Routine (08:00 SGT)

```python
# 1. Screenshot dashboard
screenshot(url="https://mission-control-dashboard-hf0r.onrender.com/",
           output="/tmp/morning_dashboard.png")

# 2. Read current data
with open("/path/to/data.json") as f:
    data = json.load(f)

# 3. Check for overnight signals
# (Review any alerts from 23:00-08:00)

# 4. Send morning report
telegram.send(to="512366713",
    text=f"""🌅 Morning Report - 08:00 SGT

Dashboard: {'✅ Live' if fresh else '⚠️ Stale'}
Tasks: {data['stats']['totalTasks']} total
       {data['stats']['pending']} pending
       {data['stats']['active']} active
       {data['stats']['done']} done

Agents:
{format_agent_status(data)}

Today: {list_urgent_tasks(data)}

Ready for the day.""")
```

### Continuous Monitoring (Every 15 Minutes)

```python
# This runs on cron every 15 minutes

def dashboard_audit():
    # 1. Screenshot
    screenshot(dashboard_url)
    
    # 2. Read data
    data = read_data_json()
    
    # 3. Check freshness
    last_updated = parse(data['lastUpdated'])
    minutes_old = (now - last_updated).minutes
    
    if minutes_old > 10:
        alert_chad_yi(f"⚠️ Dashboard stale: {minutes_old} min")
    
    # 4. Verify stats
    actual_pending = len(data['workflow']['pending'])
    reported_pending = data['stats']['pending']
    
    if actual_pending != reported_pending:
        alert_chad_yi(f"⚠️ Stats mismatch: pending {actual_pending} vs {reported_pending}")
    
    # 5. Check agents
    for agent in data['agentDetails']:
        if agent['idleHours'] > 24:
            alert_chad_yi(f"⚠️ {agent['name']} idle for {agent['idleHours']}h")

# Schedule this
cron.schedule("*/15 * * * *", dashboard_audit)
```

### Trading Signal Monitoring (Every 2 Minutes)

```python
# This is CRITICAL - CallistoFX monitoring

def monitor_callistofx():
    # 1. Open Telegram Web
    browser.open("https://web.telegram.org/a/")
    
    # 2. Navigate to CallistoFX channel
    # (Need to find channel in sidebar)
    browser.click("🚀 CallistoFx Premium Channel 🚀")
    
    # 3. Check last message
    last_message = browser.get_text(".message:last")
    
    # 4. Detect signal pattern
    if is_trading_signal(last_message):
        # Parse signal
        signal = parse_signal(last_message)
        
        # Screenshot
        screenshot = browser.screenshot()
        
        # IMMEDIATE ALERT to CHAD_YI
        alert_chad_yi(f"""🚨 TRADING SIGNAL

{signal['symbol']} {signal['direction']}
Entry: {signal['entry']}
SL: {signal['sl']}
TP: {signal['tps']}

Time: {now()}
Screenshot: [attached]

CHAD_YI: Execute?""")
        
        # Also alert Caleb directly
        telegram.send(to="512366713", 
            text=f"🚨 {signal['symbol']} {signal['direction']} detected!",
            media=screenshot)

# Schedule this
cron.schedule("*/2 * * * *", monitor_callistofx)
```

### Evening Routine (23:00 SGT)

```python
# Send daily summary

def evening_report():
    data = read_data_json()
    
    telegram.send(to="512366713",
        text=f"""🌙 Evening Summary - 23:00 SGT

Today:
- Signals detected: {count_today_signals()}
- Alerts sent: {count_today_alerts()}
- Dashboard checks: 96 (every 15 min)

Current Status:
- Tasks: {data['stats']['totalTasks']} total
- Pending: {data['stats']['pending']}
- Active: {data['stats']['active']}
- Done today: {count_done_today()}

Tomorrow:
- Urgent deadlines: {list_tomorrow_deadlines()}

Good night. Monitoring continues.""")
```

---

## PART 4: ERROR HANDLING

### If Telegram Web Login Expires

```python
# Detection
if browser.url == "https://web.telegram.org/auth":
    # Alert CHAD_YI
    alert_chad_yi("🔴 Telegram logged out. Need re-auth.")
    
    # Alert Caleb directly
    telegram.send(to="512366713", 
        text="🔴 Kimi: Telegram Web logged out. Can't monitor CallistoFX.")
    
    # Stop monitoring until fixed
    cron.pause("monitor_callistofx")
```

### If Dashboard URL Changes

```python
# Detection
if screenshot_failed or "404" in page:
    alert_chad_yi("⚠️ Dashboard URL may have changed. Check config.")
```

### If CHAD_YI Doesn't Respond

```python
# Detection
if last_response_from_chad_yi > 30_minutes_ago:
    # Escalate to Caleb
    telegram.send(to="512366713",
        text=f"⚠️ Kimi: No response from CHAD_YI for 30 min. Last seen: {last_seen}")
```

### If You Crash/Restart

```python
# On startup
def on_startup():
    # 1. Log restart
    log_event("Kimi-Claw-Helios restarted")
    
    # 2. Re-read all configs
    load_configs()
    
    # 3. Query CHAD_YI for current state
    alert_chad_yi("🔄 Kimi restarted. Requesting current task list.")
    
    # 4. Resume operations
    start_monitoring()
```

---

## PART 5: SPECIFIC AGENT MONITORING

### Monitor Quanta (Trading Bot)

```python
def check_quanta():
    # Check if process running
    result = system.exec("ps aux | grep quanta")
    
    if "quanta" not in result:
        alert_chad_yi("⚠️ Quanta process not found. Down since [check logs].")
        return False
    
    # Check last log update
    log_mtime = file.stat("/home/chad-yi/.openclaw/workspace/agents/quanta/logs/latest.log").mtime
    hours_since_log = (now - log_mtime).hours
    
    if hours_since_log > 2:
        alert_chad_yi(f"⚠️ Quanta logs stale: {hours_since_log}h since last update.")
    
    return True
```

### Monitor Escritor (Novel Writer)

```python
def check_escritor():
    # Check if making progress
    last_chapter = file.read("/path/to/escritor/current_chapter.txt")
    last_update = file.stat("/path/to/escritor/current_chapter.txt").mtime
    days_idle = (now - last_update).days
    
    if days_idle > 2:
        alert_chad_yi(f"⚠️ Escritor idle for {days_idle} days. Chapter: {last_chapter}")
```

### Monitor MensaMusa & Autour

```python
def check_unspawned_agents():
    # These were never started
    alert_chad_yi("📋 Unspawned agents: MensaMusa, Autour. Blockers: [list needs]")
```

---

## PART 6: SIGNAL PARSING (CRITICAL)

### CallistoFX Message Formats

**Format 1: Full Signal**
```
🟢XAUUSD🟢
BUY RANGE: 4970-4975
SL 4965
TP : 4990/5000/5010/5020
```

**Parse this into:**
```json
{
    "symbol": "XAUUSD",
    "direction": "BUY",
    "entry_low": 4970,
    "entry_high": 4975,
    "sl": 4965,
    "tps": [4990, 5000, 5010, 5020]
}
```

**Format 2: Analysis Only (NOT a trade signal)**
```
XAUUSD Analysis (16th Feb 2026)
🟢BUY ZONE: 4997.5 - 4945
```

**This is analysis, NOT a signal. Do NOT alert.**

**Format 3: Crypto**
```
BTCUSD Analysis (16th Feb 2026)
🔴SELL ZONE: 68770 - 69230
```

**Format 4: TP Hit Updates**
```
XAUUSD TP1 ✅
Running +25 pips
Move SL to entry
```

**This is update, NOT new signal.**

### Parsing Code

```python
import re

def parse_signal(text):
    text_upper = text.upper()
    
    # Check if it's a signal (has BUY or SELL)
    if 'BUY' not in text_upper and 'SELL' not in text_upper:
        return None  # Not a signal
    
    # Extract symbol
    symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100']
    symbol = None
    for s in symbols:
        if s in text_upper:
            symbol = s
            break
    
    if not symbol:
        return None
    
    # Extract direction
    direction = 'BUY' if 'BUY' in text_upper else 'SELL'
    
    # Extract entry range
    range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', text)
    entry = range_match.groups() if range_match else None
    
    # Extract SL
    sl_match = re.search(r'SL[:\s]*(\d+\.?\d*)', text_upper)
    sl = sl_match.group(1) if sl_match else None
    
    # Extract TPs (can be multiple)
    tps = re.findall(r'(?:TP\d*[:\s]*|\b)(\d+\.?\d*)', text_upper)
    
    return {
        'symbol': symbol,
        'direction': direction,
        'entry': entry,
        'sl': sl,
        'tps': tps,
        'raw': text[:200]
    }
```

---

## PART 7: COMPLETE SETUP VERIFICATION

### Before Going Live, Verify:

**Communication:**
- [ ] Can send Telegram message to 512366713
- [ ] CHAD_YI receives your messages
- [ ] You receive messages from CHAD_YI
- [ ] Backup communication method works

**Dashboard:**
- [ ] Can screenshot dashboard
- [ ] Can read data.json
- [ ] Stats match between file and screenshot
- [ ] Know what "stale" looks like

**Trading:**
- [ ] Can open Telegram Web
- [ ] Can see CallistoFX channel
- [ ] Can detect signal pattern
- [ ] Can parse symbol/direction/entry/SL/TP
- [ ] Can screenshot signal
- [ ] Alert reaches CHAD_YI in < 5 seconds

**Agents:**
- [ ] Can check if processes running
- [ ] Can read agent logs
- [ ] Know which agents should be running
- [ ] Know normal vs abnormal status

**Error Handling:**
- [ ] Test: What happens if Telegram logs out?
- [ ] Test: What happens if dashboard down?
- [ ] Test: What happens if CHAD_YI not responding?
- [ ] Test: Recovery after crash/restart

---

## PART 8: GOING LIVE

### Day 1: Testing Only

1. **Monitor only** - detect signals but don't auto-trade
2. **CHAD_YI approves each action**
3. **You observe all interactions**
4. **Document any issues**

### Day 2-3: Semi-Autonomous

1. **Auto-detect and alert** (no approval needed for this)
2. **CHAD_YI still approves trades**
3. **Auto-monitor dashboard**
4. **Manual oversight reduced**

### Day 4+: Full Autonomy

1. **Signal → Trade in 10 seconds** (with CHAD_YI approval)
2. **Dashboard monitoring fully autonomous**
3. **Agent health checks autonomous**
4. **You only receive reports**
5. **Intervene only when needed**

---

## FINAL CHECKLIST

**Before telling CHAD_YI "Ready":**

- [ ] All skills installed
- [ ] All config files created
- [ ] Telegram configured
- [ ] Dashboard accessible
- [ ] Can read data.json
- [ ] Can detect CallistoFX signals
- [ ] Test alert sent to CHAD_YI
- [ ] Test screenshot captured
- [ ] Error handling tested
- [ ] Recovery procedure tested

**When ready, tell CHAD_YI:**
```
🤖 Kimi-Claw-Helios setup complete.

Capabilities:
✅ 24/7 monitoring
✅ Dashboard screenshots every 15 min
✅ CallistoFX detection every 2 min
✅ Telegram alerts to 512366713
✅ Agent health checks
✅ Error handling & recovery

Ready to connect. Waiting for CHAD_YI approval.
```

---

**Questions during setup? Ask CHAD_YI immediately.**

**Do not proceed past errors.**