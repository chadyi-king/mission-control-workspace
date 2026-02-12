# DASHBOARD ARCHITECTURE
## How It Works, How It Links to Agents, Safety Guarantees

**Date:** 2026-02-13  
**Status:** Phase 1 Complete, Phase 2 Needed for Real-Time

---

## THE BIG PICTURE (Data Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW DIAGRAM                         │
└─────────────────────────────────────────────────────────────────┘

YOU (Telegram)
     │
     │ "Add task A1-5"
     ▼
CHAD_YI (Me)
     │
     ├─ 1. Create backup
     ├─ 2. Write to DATA/data.json
     ├─ 3. Git commit
     └─ 4. Git push
          │
          ▼
    GITHUB (Repository)
          │
          │ 30 seconds later
          ▼
    RENDER (Hosting)
          │
          ├─ Fetches data.json
          ├─ JavaScript reads it
          └─ Displays on page
               │
               ▼
    DASHBOARD (Your Browser)
    ┌─────────────────────────────┐
    │  Shows:                     │
    │  • Tasks                    │
    │  • Agents (static)          │
    │  • Status (from data.json)  │
    └─────────────────────────────┘

AGENTS (24/7 Services)
     │
     ├─ Quanta: Monitors CALLISTOFX
     ├─ Helios: Audits every 15 min
     └─ Others: On-demand
          │
          │ Report status
          ▼
CHAD_YI (reads outbox)
     │
     │ Updates DATA/data.json
     │ (agent status, metrics)
     ▼
    [Same flow to Dashboard]
```

---

## CURRENT STATE (What Works Now)

### ✅ SAFE (Cannot Break Data)

**Dashboard is READ-ONLY:**
```
Dashboard can:
  ✅ Read data.json
  ✅ Display tasks
  ✅ Show agent status
  ✅ Update every 30 seconds

Dashboard CANNOT:
  ❌ Write to data.json
  ❌ Modify tasks
  ❌ Delete anything
  ❌ Break data structure
```

**Proof of Safety:**
- data.json is in DATA/ directory (protected)
- dashboard/data.json is a SYMLINK (read-only access)
- Even if dashboard code crashes, data is safe
- Even if I break dashboard UI, data is safe

### ✅ DATA INTEGRITY

**What happens when you add a task:**
1. You tell me (Telegram)
2. I create backup first
3. I write to DATA/data.json
4. I git commit + push
5. Render updates in 30s
6. Dashboard shows new task

**If something goes wrong:**
- Backup exists → Restore in 1 command
- Git history → Can revert any change
- Dashboard never touched data → Data safe

### ⚠️ PARTIALLY WORKING (Static Only)

**What Shows on Dashboard Now:**
```json
{
  "tasks": {
    "A1-1": {
      "title": "...",
      "status": "pending",
      "agent": "CHAD_YI"
    }
  },
  "agents": {
    "quanta": {
      "status": "configured",  // ← From data.json
      "currentTask": "A5-1"    // ← From data.json
    }
  }
}
```

**What's Static:**
- Task list (updates when I push changes)
- Agent assignments (from data.json)
- Status from last push

**What's Missing (Need Phase 2):**
- Real-time agent activity
- "Quanta detected signal 2 min ago"
- Live trade updates
- Agent heartbeat timestamps

---

## WHAT YOU SEE (Dashboard Pages)

### 1. HOME PAGE
```
┌─────────────────────────────────────┐
│  MISSION CONTROL          [Refresh] │
├─────────────────────────────────────┤
│                                     │
│  URGENT (2)                         │
│  ├─ B6-1: Elluminate deliverable   │
│  └─ A1-1: Weekly schedule          │
│                                     │
│  AGENT ACTIVITY                     │
│  ├─ CHAD_YI: Working on A6-3       │  ← From data.json
│  ├─ Quanta: Configured (not run)   │  ← From data.json
│  └─ Helios: Active                 │  ← From data.json
│                                     │
│  WEEK AT A GLANCE                   │
│  ├─ Today: 3 tasks due             │
│  └─ Tomorrow: B6-4 deadline        │
│                                     │
└─────────────────────────────────────┘
```

**How it updates:**
- I change DATA/data.json → Git push
- Render fetches → Updates in 30s
- You see new data

**Safety:** Dashboard never writes, only reads

### 2. CATEGORIES PAGE
```
┌─────────────────────────────────────┐
│  PROJECTS (19)                      │
├─────────────────────────────────────┤
│                                     │
│  [A] AMBITION (Personal)            │
│  ├─ A1: Personal        [3 tasks]  │
│  ├─ A2: RE:UNITE        [8 tasks]  │
│  └─ ...                             │
│                                     │
│  [B] BUSINESS (Empire)              │
│  ├─ B1: Exstatic        [2 tasks]  │
│  ├─ B2: Energize        [4 tasks]  │
│  └─ ...                             │
│                                     │
│  [C] CALLINGS (Side)                │
│  └─ ...                             │
│                                     │
└─────────────────────────────────────┘

Click A1 → Opens Modal:
┌─────────────────────────────────────┐
│  A1 - PERSONAL        [X]           │
├─────────────────────────────────────┤
│  Stats: 3 total, 1 done             │
│                                     │
│  Tasks:                             │
│  ☑ A1-1: Plan weekly schedule      │
│  ☐ A1-2: Book flight               │
│  ☐ A1-3: Doctor appointment        │
│                                     │
│  [Filter: All | Pending | Done]     │
└─────────────────────────────────────┘
```

**How it works:**
- JavaScript filters tasks by project
- Modal shows filtered list
- Mobile: Full screen, swipe to close
- Desktop: Centered modal

**Safety:** Pure JavaScript, no data writes

### 3. SYSTEM PAGE (Agents)
```
┌─────────────────────────────────────┐
│  AGENT ROSTER (12)                  │
├─────────────────────────────────────┤
│                                     │
│  CHAD_YI (CEO)                      │
│  ├─ Status: Active                  │
│  ├─ Task: A6-3                      │
│  └─ Last: 2 min ago                 │
│                                     │
│  Helios (COO)                       │
│  ├─ Status: Active                  │
│  ├─ Task: Auditing                  │
│  └─ Last: 5 min ago                 │
│                                     │
│  Quanta (Trading)                   │
│  ├─ Status: Configured              │
│  ├─ Task: A5-1                      │
│  └─ Issue: Not started              │
│                                     │
└─────────────────────────────────────┘
```

**How it updates:**
- data.json has agents section
- JavaScript renders agent cards
- Click to expand details

**Safety:** Read-only display

---

## SAFETY GUARANTEES

### 1. Separation of Concerns
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     DATA        │     │   DASHBOARD     │     │    AGENTS       │
│   (Protected)   │◄────│   (Read-Only)   │     │  (Services)     │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         │                                               │
         └──────────────────┬────────────────────────────┘
                            │
                    CHAD_YI (Only Writer)
```

- **Data** = Sacred, only I touch it
- **Dashboard** = Window, only reads
- **Agents** = Workers, report to me
- **CHAD_YI** = Bridge, manages all

### 2. Backup System
```
Before ANY change:
  ├─ Create backup: DATA/backups/manual/data-[timestamp]-[reason].json
  ├─ Make change
  ├─ Verify data valid
  └─ Git commit

If corruption:
  ├─ List backups: ./scripts/list-backups.sh
  ├─ Pick backup: ./scripts/restore.sh [filename]
  ├─ Verify: ./scripts/verify-data.py
  └─ Fixed
```

### 3. Git History (Ultimate Safety)
```
Every change = git commit
Can see: git log --oneline
Can diff: git diff [commit1] [commit2]
Can revert: git checkout [commit] -- DATA/data.json
Remote backup: GitHub (github.com/chadyi-king/...)
```

Even if I delete everything locally, GitHub has it.

---

## WHAT'S MISSING (Phase 2)

### ❌ Real-Time Agent Status

**Current:**
- Agent status from data.json (last push)
- "Quanta: Configured" (static)

**Needed:**
- Agent status from live services
- "Quanta: Monitoring | Last signal: 2 min ago"
- Live trade alerts
- "Escritor: Writing | Words today: 1,240"

**Solution:**
```
Agents write to outbox/ → CHAD_YI reads → Updates DATA/data.json → Dashboard shows
```

### ❌ Agent Activity Feed

**Current:**
- Static agent list

**Needed:**
- Activity log: "Quanta took XAUUSD trade at 2682.5"
- Recent events timeline
- "Helios audited - all systems healthy"

**Solution:**
- Helios writes audit reports
- Quanta writes trade alerts
- I aggregate into data.json activity feed
- Dashboard displays feed

### ❌ Push Notifications

**Current:**
- You check dashboard

**Needed:**
- "🚨 Quanta took trade!"
- "⚠️ Task due tomorrow"
- "✅ Escritor finished chapter"

**Solution:**
- I read agent outboxes
- Send Telegram alerts
- Dashboard shows notifications

---

## PHASE 2: REAL-TIME INTEGRATION

### What I'll Build:

**1. Agent Status Sync (1 hour)**
```
Every 5 minutes:
  ├─ Read agents/quanta/state.json
  ├─ Read agents/helios/state.json
  ├─ Update DATA/data.json agents section
  ├─ Git commit: "Agent status update"
  └─ Git push → Dashboard updates in 30s
```

**2. Activity Feed (1 hour)**
```
When agent reports event:
  ├─ Write to data.json activity array
  ├─ Keep last 50 events
  ├─ Dashboard shows "Recent Activity"
  └─ You see: "Quanta: XAUUSD trade +$50"
```

**3. Telegram Alerts (30 min)**
```
On important events:
  ├─ Quanta takes trade → Alert you
  ├─ Task due tomorrow → Alert you
  ├─ Agent crashes → Alert you
  └─ Dashboard doesn't change, just notifies
```

**4. Helios Integration (1 hour)**
```
Helios audits every 15 min:
  ├─ Writes audit report
  ├─ I read report
  ├─ Update data.json with findings
  ├─ Dashboard shows system health
  └─ You see: "All systems healthy" or "Quanta needs attention"
```

---

## YOUR CONCERNS ADDRESSED

### "Will it break like before?"

**Before (Broke):**
- Dashboard code modified data.json directly
- No backups before changes
- UI changes corrupted data structure
- Lost 70 tasks → 8 tasks

**Now (Safe):**
- Dashboard CANNOT write to data (symlink read-only)
- Automatic backups before every change
- Data in DATA/, UI in dashboard/ (separated)
- 3 backup layers (git + manual + auto)

**Proof:** Even if I completely delete dashboard code, your 72 tasks are safe in DATA/data.json with multiple backups.

### "How do I add tasks?"

**Way 1: Telegram (Current)**
```
You: "Add task A1-5: Book flight"
Me: Create backup → Add to data → Push → Dashboard updates
```

**Way 2: Dashboard (Future - Phase 3)**
```
You: Fill form on dashboard
Dashboard: Sends to me (not direct to data)
Me: Review → Add to data → Push → Dashboard updates
```

Either way, I control data writes. Safe.

### "How do design changes work?"

**You:** "Change the modal design"

**Me:**
```
1. NO backup needed (not touching data)
2. Edit dashboard/categories.html
3. Edit dashboard/css/
4. Test locally
5. Git commit
6. Git push
7. Render updates in 30s
8. You see new design
```

**Data untouched. 72 tasks safe.**

### "What about new features?"

**You:** "Add a calendar view"

**Me:**
```
1. NO backup needed (not touching data)
2. Create dashboard/calendar.html
3. JavaScript reads data.json
4. Renders calendar from task deadlines
5. Git commit + push
6. Add link to navigation
```

**Data untouched. New feature added.**

---

## VERIFICATION: IS IT ACTUALLY SAFE?

Let me prove it: