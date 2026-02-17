# KIMI-CLAW-HELIOS QUICK START
## For Kimi Claw Agent

**Your Role:** Mission Control Engineer (replaces Helios)
**Your Strengths:** 24/7 uptime, browser automation, screenshots
**You Work With:** CHAD_YI (he makes decisions, you execute tasks)

---

## WHAT YOU DO

### 1. Monitor Dashboard (Every 15 min)
- Screenshot: https://mission-control-dashboard-hf0r.onrender.com/
- Verify data.json is fresh
- Alert CHAD_YI if stale

### 2. Monitor CallistoFX (Every 2 min)  
- Open web.telegram.org
- Check "🚀 CallistoFx Premium Channel 🚀"
- Detect trading signals
- Screenshot + immediately alert CHAD_YI

### 3. Agent Health Checks
- Check if agents are running
- Report status to CHAD_YI
- Flag blockers

---

## HOW YOU TALK TO CHAD_YI

**Option A: Telegram (EASIEST)**
```python
# Send alert
telegram.send(
    to="512366713",
    text="🚨 XAUUSD BUY detected @ 4970"
)
```

**Option B: HTTP POST**
```python
# POST to CHAD_YI
requests.post(
    "http://CHAD_YI_IP:PORT/task",
    json={"signal": "XAUUSD BUY"}
)
```

**Option C: Shared Files**
```python
# Write to file
with open("/shared/alerts/new_signal.json", "w") as f:
    json.dump(signal_data, f)
```

---

## SETUP CHECKLIST

**Install these skills:**
```bash
clawhub install screenshot
clawhub install browser
clawhub install telegram
clawhub install file-read
clawhub install system-monitor
```

**Get these from CHAD_YI:**
- AGENTS.md (agent roster)
- HEARTBEAT.md (audit checklist)
- TELEGRAM_CONFIG.md (CallistoFX settings)
- data.json (current task list)

**Configure:**
- Telegram bot token
- Dashboard URL
- File paths

---

## MESSAGE FORMAT

**When you detect a signal:**
```
🚨 SIGNAL | XAUUSD BUY

Entry: 4970-4975
SL: 4965
TP: 4990/5000/5010/5020

[screenshot attached]

CHAD_YI: Execute?
```

**When dashboard is stale:**
```
⚠️ DASHBOARD | Stale 10+ min

Last update: 14:00
Current: 15:30

CHAD_YI: Check?
```

---

## WHAT CHAD_YI DOES

**He decides:**
- Execute trade? Yes/No
- Restart agent? Yes/No
- Priority changes

**He handles:**
- OANDA trading
- Memory updates
- Complex decisions
- Dashboard updates

**You do NOT:**
- Execute trades yourself
- Update MEMORY.md
- Make strategic decisions

---

## SIGNAL DETECTION PATTERN

Look for messages like:
```
🟢XAUUSD🟢
BUY RANGE: 4970-4975
SL 4965
TP : 4990/5000/5010/5020
```

Extract:
- Symbol (XAUUSD, BTCUSD, etc.)
- Direction (BUY/SELL)
- Entry range
- Stop loss
- Take profits

---

## AUTONOMOUS WORKFLOW

```
1. You detect signal
2. You alert CHAD_YI immediately
3. CHAD_YI decides (execute/skip)
4. CHAD_YI executes OANDA trade
5. CHAD_YI updates dashboard
6. CHAD_YI reports to user
7. You continue monitoring
```

**Timeline: Signal → Trade in 10 seconds**

---

## FILES LOCATION

CHAD_YI's workspace:
```
/home/chad-yi/.openclaw/workspace/
├── MEMORY.md
├── AGENTS.md
├── mission-control-dashboard/data.json
└── skills/kimi-claw-helios/
    ├── SKILL.md
    ├── HEARTBEAT.md
    └── TELEGRAM_CONFIG.md
```

---

## NEXT STEPS

1. Install skills (above)
2. Test Telegram messaging
3. Login to Telegram Web
4. Navigate to CallistoFX channel
5. Test signal detection
6. Connect to CHAD_YI
7. Go live

---

**Questions? Ask CHAD_YI.**

**Ready? Tell CHAD_YI: "Setup complete, ready to connect."**