# HEARTBEAT.md - Kimi-Claw-Helios
# 15-Minute Audit Checklist

## Schedule
- Every 15 minutes
- Runs 24/7
- Reports to CHAD_YI

---

## Checks

### 1. Dashboard Status
- [ ] Screenshot https://mission-control-dashboard-hf0r.onrender.com/
- [ ] Verify `lastUpdated` timestamp is recent (< 5 min)
- [ ] Read actual data.json from workspace
- [ ] Compare: Screenshot stats vs data.json stats
- [ ] Flag any discrepancies

### 2. Task Count Verification
```bash
# Read actual data
data.json stats should match:
- Total tasks
- Pending count
- Active count
- Review count
- Done count
```

### 3. Agent Status
- [ ] Check if agents are running:
  ```bash
  ps aux | grep quanta
  ps aux | grep helios
  ps aux | grep escritor
  ```
- [ ] Check log file updates (last modified time)
- [ ] Calculate idle time for each agent

### 4. Urgent Deadlines
- [ ] Check tasks with deadlines < 24h
- [ ] Alert if anything overdue
- [ ] Flag approaching deadlines

### 5. Blockers
- [ ] Check inputsNeeded array
- [ ] If items blocked > 7 days → urgent alert
- [ ] Summarize what each blocker needs

### 6. Telegram Monitor (Every 2 min, separate cron)
- [ ] Open web.telegram.org
- [ ] Check CallistoFX channel
- [ ] Detect new trading signals
- [ ] Screenshot + alert CHAD_YI immediately

---

## Report Format

Send to CHAD_YI (Telegram 512366713):

```
🤖 Kimi-Claw-Helios Report - HH:MM SGT

Dashboard: [✅/⚠️/❌] (last update X min ago)
Tasks: Total X | Pending X | Active X | Done X

Agents:
  [Agent] - [Status] | [Task] | [Idle Xh]

Urgent: [List any <24h deadlines]

Blockers: [List any stalled >7 days]

Trading: [Any signals detected]
```

---

## Alert Thresholds

- **Dashboard stale > 10 min**: 🔴 Critical
- **Agent down**: 🔴 Critical  
- **Deadline < 8h**: 🔴 Critical
- **Blocker > 7 days**: 🟡 Warning
- **Stats mismatch**: 🟡 Warning

---

## Actions on Alerts

1. **Critical**: Send immediate Telegram message to CHAD_YI
2. **Warning**: Include in next scheduled report
3. **Signal detected**: Immediate alert with screenshot

---

## Files to Monitor

```
/home/chad-yi/.openclaw/workspace/
├── mission-control-dashboard/data.json
├── agents/quanta/logs/
├── agents/helios/logs/
└── memory/YYYY-MM-DD.md
```

---

## Communication Rules

- **Do NOT** update tasks/status yourself
- **Only CHAD_YI** updates data.json
- **Your job**: Monitor, detect, report
- **Alert immediately** for critical issues
- **Batch warnings** in scheduled reports