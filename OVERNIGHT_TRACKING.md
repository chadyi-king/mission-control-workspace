# OVERNIGHT TRACKING
## What Happens While You Sleep

**Date:** 2026-02-13  
**Time Now:** 01:45 SGT  
**Your Action:** Install Quanta service, then sleep  
**Morning Report:** Run `./scripts/morning-report.sh`

---

## AUTOMATED SYSTEMS (Running 24/7)

### 1. Helios Auditor (✅ ACTIVE)
**Status:** Running via systemd  
**Frequency:** Every 15 minutes  
**What it does:**
- Checks DATA/data.json integrity
- Audits all agents (CHAD_YI, Quanta, etc.)
- Creates audit reports
- Detects issues

**Where to check:**
```bash
# See latest audit
ls -lt agents/helios/outbox/audit-*.json | head -1

# View report
cat agents/helios/outbox/audit-[latest].json
```

### 2. Quanta Monitor (⏳ PENDING YOUR INSTALL)
**Status:** Ready but not running (needs sudo install)  
**Once installed:**
- Monitors CALLISTOFX 24/7
- Logs ALL messages
- Detects signals
- Creates trade plans

**Install with:**
```bash
sudo cp agents/quanta/quanta.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quanta
sudo systemctl start quanta
```

---

## WHAT TO CHECK IN MORNING

### Quick Check (1 minute):
```bash
cd /home/chad-yi/.openclaw/workspace
./scripts/morning-report.sh
```

### Detailed Check (5 minutes):

**1. Helios Audits:**
```bash
# How many audits overnight?
ls agents/helios/outbox/audit-2026-02-13*.json | wc -l

# Any critical issues?
grep -l "critical" agents/helios/outbox/audit-2026-02-13*.json
```

**2. Quanta Activity:**
```bash
# Messages logged
wc -l agents/quanta/logs/all_messages.jsonl

# Signals detected
grep '"type": "signal"' agents/quanta/logs/all_messages.jsonl | wc -l

# Trade plans created
ls agents/quanta/outbox/trade-*.json 2>/dev/null | wc -l
```

**3. Data Integrity:**
```bash
python3 scripts/verify-data.py
```

---

## IF SOMETHING BREAKS OVERNIGHT

### Helios Stops:
```bash
sudo systemctl status helios
sudo systemctl restart helios
```

### Quanta Stops:
```bash
sudo systemctl status quanta
sudo systemctl restart quanta
```

### Data Corruption:
```bash
./scripts/restore.sh [backup-file]
```

---

## WHAT I (CHAD_YI) CANNOT DO WHILE YOU SLEEP

**I cannot:**
- Respond to messages (only when you message me)
- Make decisions (need your input)
- Fix complex issues (need to investigate)
- Code new features (need active session)

**I CAN (via automated systems):**
- Helios audits (automated)
- Quanta monitoring (once you install)
- Data backups (if configured)
- Service restarts (if crashed)

---

## WHAT I WILL DO FIRST THING IN MORNING

**When you message me:**
1. Read overnight audit reports
2. Check Quanta logs
3. Verify data integrity
4. Report status
5. Address any issues

**Report format:**
```
Morning Report - [Time] SGT

Helios Audits: [X] completed overnight
Issues Found: [None / List]
Quanta Activity: [X] messages, [Y] signals
Data Status: [OK / Issues]
Actions Needed: [None / List]
```

---

## YOUR CHECKLIST BEFORE SLEEP

- [ ] Install Quanta service (sudo commands above)
- [ ] Verify Helios running: `systemctl status helios`
- [ ] Note any concerns for morning
- [ ] Sleep well

---

## TOMORROW'S PRIORITIES

**Morning (First 30 min):**
1. Review overnight activity
2. Check for issues
3. Address any blockers

**If Time Permits:**
- OANDA integration (you'll provide credentials)
- Dashboard System Health section
- Test full trade execution

---

**Rest well. Systems are in place. I'll report in the morning.**
