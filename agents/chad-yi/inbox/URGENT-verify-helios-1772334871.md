# 🔴 URGENT — Helios Verification Task
**From:** Copilot (via Caleb)  
**Time:** 2026-02-28 23:00 SGT  
**Priority:** HIGH — Caleb is away, needs you to verify this

---

## What Was Fixed

Helios now auto-syncs the dashboard every 15 minutes. Here's what changed:

1. **Helios writes `data.json`** → git commits → pushes to GitHub → Render deploys → Dashboard updates
2. **Source of truth is `ACTIVE.md`** — that's the ONE file you edit to update tasks
3. **You do NOT touch `data.json`** — Helios owns that

---

## YOUR VERIFICATION TASKS

### Step 1 — Confirm Helios is running
Run this command:
```bash
pgrep -fa "helios-v2.py" && echo "✅ HELIOS RUNNING" || echo "❌ HELIOS DEAD"
```

### Step 2 — Check last sync time
```bash
tail -5 /home/chad-yi/.openclaw/workspace/agents/helios/helios.log
```
You should see `[sync] ✅ Pushed to GitHub` within the last 15 minutes.

### Step 3 — Check dashboard data is fresh
```bash
python3 -c "import json; d=json.load(open('/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json')); print('Last updated:', d['lastUpdated']); print('Updated by:', d['updatedBy'])"
```
Should show `updatedBy: helios-v2` and a timestamp from today.

### Step 4 — Check live dashboard
Open: https://red-sun-mission-control.onrender.com
The "Last Updated" should show today's date.

### Step 5 — Test a task update (IMPORTANT)
1. Open: `/home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md`
2. Add a test task under ACTIVE:
   ```
   | TEST-1 | Verification test by Chad | CHAD_YI | 🔄 IN_PROGRESS |
   ```
3. Save the file
4. Wait up to 15 minutes
5. Check the dashboard — the `lastUpdated` timestamp should change

---

## IF HELIOS IS DEAD — Restart it

```bash
nohup /home/chad-yi/.venv/bin/python /home/chad-yi/.openclaw/workspace/agents/helios/helios-v2.py >> /home/chad-yi/.openclaw/workspace/agents/helios/helios.log 2>&1 &
echo "Helios restarted"
```

---

## REPORT BACK TO CALEB ON TELEGRAM

Once you've verified, message Caleb (@MrCalbeeChips) on Telegram with:

```
✅ Helios verified. Running PID [X]. Last sync: [timestamp]. Dashboard updated at [time]. System is live.
```

Or if something is broken:
```
❌ Issue found: [describe what failed]. Need help.
```

---

## KEY FILE LOCATIONS

| What | Where |
|------|-------|
| Edit tasks here | `/home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md` |
| Helios log | `/home/chad-yi/.openclaw/workspace/agents/helios/helios.log` |
| Dashboard data | `/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json` |
| Full prompt | `/home/chad-yi/.openclaw/CHAD_TASK_UPDATE_PROMPT.md` |

