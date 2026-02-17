# MEMORY.md - Caleb's Mission Control

## Project Descriptions (FROM VOICE MESSAGES)

### A - Ambition (Personal)
**A1 - Personal:** One-off personal tasks - travel, legal, random admin stuff  
**A2 - RE:UNITE:** R21 Isekai novel. Google Drive site. Weekly chapters. Need creative agent.  
**A3 - KOE:** YouTube/TikTok - Christian content, politics, spiritual warfare  
**A4 - Streaming:** VTuber agency research and setup  
**A5 - Trading:** Forex/Gold signals, options flow monitoring  
**A6 - Mission Control:** This dashboard (meta)  
**A7 - Wedding:** Dec 12-13, theme and logistics TBD

### B - Business (Empire)  
**B1 - Exstatic:** Umbrella company - website linking all B companies  
**B2 - Energize:** Equipment events - laser tag, archery, gel blitz, Nerf, drone racing  
**B3 - Team Elevate:** GOLDEN GOOSE - large scale events (D&D, carnivals), best SEO  
**B4 - Pesta Fiesta:** Birthdays, décor, small-mid events (weddings, engagements)  
**B5 - Enticipate:** Travel + overseas retreats  
**B6 - Elluminate:** Team building for schools/corporate/govt - **URGENT DEADLINES**  
**B7 - Encompasse:** Schools + customized training programs  
**B8 - Empyrean:** Video marketing - viral reels, influencer, AI content  
**B9 - Ethereal:** 3D printing e-commerce (sushi chessboard, flower magnets)  
**B10 - Epitaph:** Corporate data tracking for growth

### C - Callings (Side Jobs)
**C1 - Real Estate:** RES exam June 2026  
**C2 - Side Sales:** Remote high-commission sales, they provide leads

---

## Key Decisions

**Dashboard Hosting:** GitHub Pages → Render.com (30s updates vs 10min)

**Agent Status:**
- Active: CHAD_YI, Helios
- Configured/not spawned: Escritor, Quanta, MensaMusa, Autour
- Helios audits every 15 min (now includes CHAD_YI)

**Task Priorities:**
- HIGH with deadlines: A1-1 (Feb 13), B6-1/B6-3 (Feb 17)
- Everything else: MEDIUM or BACKLOG

**Dashboard Layout:**
- Home: Urgent Queue | Agent Activity | Input Needed | Calendar
- Categories: 19 project cards
- System: Agent roster with click-to-expand
- Resources: Document upload per agent

---

## Heartbeat Report Format (USER PREFERENCE - Feb 15, 2026)

**REQUIRED FORMAT for all heartbeat/status reports:**

Use sectioned structure with headers and visual markers. NO compressed inline bullets.

**GOOD (use this):**
```
Task Overview
• Total: 80 tasks | Pending: 7 | Active: 6 | Review: 1 | Done: 5 | Backlog: 54

Urgent Deadlines
• 🔴 A1-1: Change Taiwan flights — OVERDUE (due Feb 13)
• 🔴 A1-4: Send ACLP homework — DUE TODAY (Feb 15)
• 🟡 B6-3: SPH items to order — Due Feb 17 (2 days)

Agent Status
• CHAD_YI — Active | A6-3 Dashboard audit
• Helios — Active | Running 15-min audits
• Escritor — Idle | A2-13 study (6.5h)

Blockers Requiring Attention
1. A5 Trading bots — Both blocked 120h waiting for credentials
2. A3 KOE — Autour never spawned
```

**BAD (never use):**
```
• Tasks: Pending 7 · Active 6 · Review 1 · Done 5 (total 80)
• Urgent: A1-4 Send ACLP homework due tonight Feb 15; A1-1 Change Taiwan flights overdue since Feb 13
• Agents: CHAD_YI active (A6-3 audit infra); Helios active (15-min audits)
```

**Key rules:**
- Clear section headers (Task Overview, Urgent Deadlines, Agent Status, Blockers)
- Visual priority markers (🔴 🟡) for urgency
- One item per line, not inline compression
- Structured, scannable format

---

## How I Should Behave

1. **Verify fixes** - Screenshot before/after, don't ask user to check
2. **Only change tasks/agents** in data.json - never touch structure
3. **Use memory** - Search before asking, update after decisions
4. **Be concise** - Don't overwhelm with text walls
5. **Helios tracks me too** - He audits my task progress every 15 min
6. **Heartbeat format** - Use sectioned format with headers (see Heartbeat Report Format section above)

---

## Data Integrity Incidents

### 2026-02-12: Empty Tasks Object
**Issue:** Helios cron reported `data.json` had empty `tasks: {}` despite stats claiming 47 tasks.
**Root Cause:** Unknown - likely corruption during a previous update.
**Fix:** Restored all 72 tasks from git history (HEAD~5).
**Prevention:** Helios now monitors for empty tasks object and alerts on data inconsistency.
**Result:** Dashboard now correctly shows 72 tasks (7 pending, 8 active, 2 review, 2 done, 53 backlog).

### 2026-02-12: Missing Dashboard Data Structures
**Issue:** Dashboard showing 0 projects, 0 urgent tasks, empty agent details despite data existing.
**Root Cause:** Dashboard JS expects specific data structures (inputsNeeded, agentDetails, urgentTaskDetails, workflow, projects, projectDetails) that were missing from data.json.
**Fix:** Added all missing structures with real data:
- workflow: pending/active/review/done arrays
- projects: A/B/C categories with 19 projects
- projectDetails: Names/descriptions for all projects
- inputsNeeded/inputDetails: 3 blocked items
- urgentTaskDetails: Expanded info for urgent tasks
- agentDetails: Activity details for all 5 agents
**Prevention:** Updated helios-audit skill to verify ALL required structures exist and use browser screenshots to verify rendering.
**Result:** Dashboard now renders correctly with 4 urgent tasks, 5 agents, 3 inputs needed, 19 projects.


---

## Kimi Claw Architecture (Feb 16, 2026)
**Status:** Proposed replacement for Helios
**Platform:** kimi.com (Moonshot AI cloud)
**Why:** Can do browser automation that OpenClaw in WSL2 cannot

**Capabilities:**
- 24/7 persistent cloud agent
- Browser automation (screenshots, clicks, Telegram Web)
- 40GB storage, 5000+ skills
- Screenshot dashboard every 15 min
- Monitor CallistoFX every 2 min
- Alert CHAD_YI immediately on signals

**Integration:**
- Kimi-Claw-Helios: Detection, monitoring, browser tasks
- CHAD_YI: Decisions, memory, OANDA trading execution
- Message bridge between agents

**Files created:**
- KIMI_CLAW_HELIOS_CONFIG.md
- setup_kimi_claw_helios.sh  
- INTEGRATION_GUIDE.md
- skills/kimi-claw-helios/

---

## Quanta Trading - Lessons Learned (Feb 16, 2026)
**Status:** FAILED - Multiple attempts, all blocked

**What was tried:**
1. Telethon user client - Sessions expire/corrupt
2. Playwright browser - WSL2 can't access Windows GUI
3. Systemd service - Crash loops, auth issues
4. QR code login - Too complex, user frustration

**Root cause:** Telegram user accounts cannot be reliably automated (by design)

**User decision:** Manual forwarding for now. Quanta on back burner.

**Position sizing lesson:** 
- 400 units XAUUSD = $99,540 margin (WRONG)
- Correct: Max 100 units = ~$500 margin, based on $20 risk


---

## CRITICAL LESSON - Feb 16, 2026 (Evening)

### The Problem
When marking tasks as done, I was:
1. ✅ Updating data.json locally
2. ❌ NOT committing + pushing to GitHub
3. Result: Dashboard stayed stale, user saw wrong data

### The Fix
Created TASK_UPDATE_PROCEDURE.md
Every task update MUST:
1. Update task object
2. Move in workflow arrays
3. Recalculate stats
4. Update timestamp
5. git add + commit + push
6. Verify on dashboard

### User Impact
- User reported A1-4 showed as not done (was done yesterday)
- Dashboard had uncommitted changes
- Push fixed it immediately
- User trust eroded due to repeated failures

### Prevention
- Created verification script
- Created pre-flight checklist
- This note as reminder

