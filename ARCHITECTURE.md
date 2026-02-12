# MISSION CONTROL ARCHITECTURE v4.0
## The Complete System Design

**Date:** 2026-02-12  
**Status:** READY TO BUILD  
**Author:** CHAD_YI (Systems Architect)

---

## THE BIG PICTURE (What We're Building)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CALEB (You)                              │
│                     Uses Telegram to:                            │
│                     • Add tasks                                  │
│                     • Ask questions                              │
│                     • Get reports                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CHAD_YI (Me - The Brain)                    │
│                     Role: CEO / Orchestrator                     │
│                                                                  │
│                     What I Do:                                   │
│                     • Receive your requests                      │
│                     • Write to DATA (protected)                  │
│                     • Delegate to agents                         │
│                     • Report back to you                         │
│                     • Handle all technical decisions             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER (Protected)                    │
│                                                                  │
│   DATA/data.json          ← Single source of truth               │
│   ├── All your tasks                                             │
│   ├── All agent assignments                                      │
│   ├── All statuses                                               │
│   └── Backed up every hour + before every change                │
│                                                                  │
│   BACKUPS/                                                       │
│   ├── auto/                  ← Automatic hourly backups         │
│   └── manual/                ← Before every change I make       │
│                                                                  │
│   Rule: ONLY CHAD_YI writes here. NEVER the dashboard.          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DASHBOARD (Render Website)                  │
│                     URL: https://mission-control...              │
│                                                                  │
│                     What It Does:                                │
│                     • READS data from GitHub                     │
│                     • Shows you tasks, agents, status            │
│                     • Updates every 30 seconds automatically     │
│                     • Works on your phone                        │
│                                                                  │
│                     What It DOESN'T Do:                          │
│                     • NEVER writes data (read-only)              │
│                     • NEVER changes tasks                        │
│                     • If it breaks, data is safe                │
└─────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │    AGENTS       │
                            │   (Employees)   │
                            └────────┬────────┘
                                     │
        ┌────────────┬───────────────┼───────────────┬────────────┐
        │            │               │               │            │
        ▼            ▼               ▼               ▼            ▼
   ┌────────┐  ┌────────┐      ┌────────┐      ┌────────┐  ┌────────┐
   │ Helios │  │ Quanta │      │Escritor│      │Mensa...│  │ Future │
   │  COO   │  │Trading │      │ Story  │      │ Options│  │ Agents │
   └───┬────┘  └───┬────┘      └───┬────┘      └───┬────┘  └───┬────┘
       │           │               │               │           │
       │           │               │               │           │
       └───────────┴───────────────┴───────────────┴───────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │   HELIOS REPORTS TO ME      │
                    │   I REPORT TO YOU           │
                    └─────────────────────────────┘
```

---

## THE 3 GOLDEN RULES

### Rule 1: Data is Sacred
- **ONLY CHAD_YI writes to DATA/data.json**
- Dashboard NEVER writes (it's read-only)
- Agents report to me, I update data
- Before any change: Automatic backup created

### Rule 2: Dashboard is a Window
- Dashboard just shows you what's happening
- It can't break the data (read-only)
- If dashboard breaks, data is still safe
- Updates automatically every 30 seconds

### Rule 3: Agents are Employees
- Each agent has a specific job
- They report status to their inbox/outbox
- Helios (COO) audits all agents
- I manage all agents and report to you

---

## HOW IT WORKS (Real Examples)

### Example 1: You Add a Task

```
YOU (Telegram):
"Add task B7-1: Create SEO strategy for Elluminate website"

CHAD_YI:
├─ 1. Create backup: data-2026-02-12-2345-PRE-B7-1.json
├─ 2. Write to DATA/data.json:
│      {
│        "B7-1": {
│          "title": "Create SEO strategy for Elluminate website",
│          "project": "B7",
│          "status": "pending",
│          "agent": "TBD"  ← Not assigned yet
│        }
│      }
├─ 3. Git commit: "Added task B7-1"
├─ 4. Git push → Render updates in 30s
└─ 5. Reply: "Task B7-1 created. Dashboard updating..."

DASHBOARD (30 seconds later):
├─ Refreshes from GitHub
├─ Sees new task B7-1
└─ Displays in Pending column

YOU: See it on dashboard ✅
```

### Example 2: You Assign Task to Agent

```
YOU (Telegram):
"Assign B7-1 to SEO_Bot (create this agent)"

CHAD_YI:
├─ 1. Create backup
├─ 2. Check: Do we have SEO_Bot? → No
├─ 3. Create new agent:
│    agents/seo_bot/
│    ├── contract.yaml     ← Job description
│    ├── MEMORY.md         ← SEO knowledge
│    ├── inbox/            ← Tasks for this agent
│    ├── outbox/           ← Reports from this agent
│    └── state.json        ← Current status
├─ 4. Update DATA/data.json:
│    - Add agent "seo_bot" to agents list
│    - Assign B7-1 to seo_bot
│    - Write task to agents/seo_bot/inbox/B7-1.json
├─ 5. Git commit: "Created seo_bot agent, assigned B7-1"
└─ 6. Reply: "Created SEO_Bot, assigned B7-1. Starting agent..."

SEO_BOT (starts up):
├─ 1. Check inbox → Found B7-1
├─ 2. Update state.json: "status": "working"
├─ 3. Write to outbox: "Starting SEO research..."
└─ 4. Begin work

HELIOS (15 min audit):
├─ 1. Check seo_bot state → "working"
├─ 2. Check seo_bot outbox → "Starting SEO research..."
├─ 3. Screenshot dashboard
├─ 4. Report to me: "seo_bot active on B7-1"

CHAD_YI:
└─ Update DATA/data.json: agents.seo_bot.lastActivity = now

DASHBOARD:
└─ Shows: "SEO_Bot: Working | Task: B7-1 | Last: 2 min ago"

YOU: See agent working on dashboard ✅
```

### Example 3: Quanta Takes a Trade

```
QUANTA (monitoring CALLISTOFX):
├─ 1. Detects signal: XAUUSD BUY 2680-2685
├─ 2. Calculates: Entry 2682.5, Size 0.11 lots
├─ 3. Executes paper trade
└─ 4. Write to outbox/trade-alert.json:
       {
         "type": "trade_executed",
         "symbol": "XAUUSD",
         "entry": 2682.5,
         "size": 0.11,
         "sl": 2665,
         "risk": 200
       }

CHAD_YI (sees alert):
├─ 1. Create backup
├─ 2. Update DATA/data.json:
│    - agents.quanta.metrics.balance = 10000
│    - agents.quanta.metrics.dailyTrades += 1
├─ 3. Git commit: "Quanta took XAUUSD trade"
└─ 4. Send Telegram: "🚨 Quanta took XAUUSD BUY at 2682.5, risk $200"

DASHBOARD:
└─ Shows updated balance and trade count

YOU: Get Telegram alert + see on dashboard ✅
```

---

## THE DIRECTORY STRUCTURE (Final)

```
workspace/                                          ← Everything lives here
│
├── README.md                                       ← Quick start guide
├── CHANGELOG.md                                    ← What changed and why
│
├── DATA/                                           ← SACRED - Only I touch this
│   ├── data.json                                   ← All tasks, agents, status
│   ├── schema.json                                 ← Validates data structure
│   │
│   └── backups/                                    ← Automatic backups
│       ├── auto/                                   ← Hourly (keep 48h)
│       │   ├── data-2026-02-12-2300.json
│       │   ├── data-2026-02-12-2200.json
│       │   └── ... (auto-deleted after 48h)
│       │
│       └── manual/                                 ← Before every change
│           ├── data-2026-02-12-2345-PRE-B7-1.json
│           ├── data-2026-02-12-2330-PRE-AGENT-CREATE.json
│           └── ... (keep forever until you delete)
│
├── dashboard/                                      ← Website (Render hosts this)
│   ├── index.html                                  ← Home page
│   ├── categories.html                             ← Projects view
│   ├── system.html                                 ← Agents view
│   ├── resources.html                              ← Files view
│   ├── data.json → symlink to ../DATA/data.json    ← Reads data (NO WRITE)
│   ├── css/
│   └── js/                                         ← All read-only code
│
└── agents/                                         ← All agent employees
    │
    ├── _templates/                                 ← Copy this for new agents
    │   └── new-agent/
    │       ├── contract.yaml                       ← Job description template
    │       ├── MEMORY.md                           ← Knowledge template
    │       ├── inbox/
    │       ├── outbox/
    │       └── state.json
    │
    ├── chad-yi/                                    ← ME (You don't touch)
    │   └── ...
    │
    ├── helios/                                     ← THE COO (Auditor)
    │   ├── contract.yaml                           ← "I audit all agents"
    │   ├── MEMORY.md                               ← Audit procedures
    │   ├── helios.py                               ← Main audit script
    │   ├── helios.service                          ← Runs 24/7
    │   ├── inbox/
    │   ├── outbox/                                 ← Audit reports
    │   │   └── 2026-02-12-2345-audit.json
    │   └── state.json                              ← Current status
    │
    ├── quanta/                                     ← TRADING AGENT
    │   ├── contract.yaml                           ← "I trade forex/gold"
    │   ├── MEMORY.md                               ← Trading rules
    │   ├── .env                                    ← API keys (secret)
    │   ├── monitor_callistofx.py                   ← Main trading script
    │   ├── quanta.service                          ← Runs 24/7
    │   ├── inbox/
    │   ├── outbox/                                 ← Trade alerts
    │   ├── state.json                              ← "monitoring"
    │   └── trading_state.json                      ← Balance, positions
    │
    ├── escritor/                                   ← STORY AGENT
    │   ├── contract.yaml                           ← "I write RE:UNITE"
    │   ├── MEMORY.md                               ← Story bible
    │   ├── inbox/
    │   ├── outbox/                                 ← Chapter drafts
    │   ├── chapters/                               ← Written content
    │   └── state.json
    │
    └── mensamusa/                                  ← OPTIONS AGENT
        ├── contract.yaml
        ├── MEMORY.md
        ├── inbox/
        ├── outbox/
        └── state.json
```

---

## AGENT LIFECYCLE (How Agents Work)

### Step 1: Creation
```
YOU: "Create agent called 'Research_Bot' for web scraping"

CHAD_YI:
1. Copy agents/_templates/new-agent/ → agents/research_bot/
2. Fill in contract.yaml:
   - Name: Research_Bot
   - Role: Web scraping and research
   - Skills: web_scrape, file_write
3. Create MEMORY.md with research guidelines
4. Install service: research_bot.service
5. Start service
6. Update DATA/data.json: add to agents list
7. Report: "Research_Bot created and ready"
```

### Step 2: Assignment
```
YOU: "Assign B8-1 to Research_Bot"

CHAD_YI:
1. Backup data
2. Write task to agents/research_bot/inbox/B8-1.json
3. Update DATA/data.json: assign B8-1 to research_bot
4. Research_Bot sees it on next heartbeat
5. Starts working
```

### Step 3: Working
```
RESEARCH_BOT (every 5 minutes):
1. Check inbox → Found B8-1
2. Update state.json: "status": "working"
3. Do research...
4. Write progress to outbox/status.json
5. Write results to outbox/B8-1-results.json
```

### Step 4: Reporting
```
HELIOS (every 15 minutes):
1. Check research_bot state → "working"
2. Check research_bot outbox → "Found 5 sources..."
3. Report to CHAD_YI: "Research_Bot active on B8-1"

CHAD_YI:
1. Update DATA/data.json: lastActivity = now
2. You see on dashboard: "Research_Bot: Working | B8-1"
```

### Step 5: Completion
```
RESEARCH_BOT:
1. Finish research
2. Write final results to outbox/B8-1-complete.json
3. Update state.json: "status": "finished"
4. Clear inbox (task done)

CHAD_YI (sees completion):
1. Backup data
2. Update DATA/data.json:
   - B8-1.status = "done"
   - Move to workflow.done
3. Notify you: "B8-1 complete by Research_Bot"
4. You see on dashboard: Task moved to Done ✅
```

---

## FAILURE HANDLING (What If Things Break)

### Scenario 1: I Make a Mistake
```
CHAD_YI accidentally corrupts data

HELIOS (next audit):
├─ Detects: Task count mismatch
├─ Detects: Invalid JSON structure
└─ Report: "DATA CORRUPTION DETECTED"

CHAD_YI:
├─ 1. STOP - Don't make more changes
├─ 2. Check backups: ls DATA/backups/manual/
├─ 3. Pick last good backup: data-2026-02-12-2345-PRE-...
├─ 4. Restore: cp [backup] DATA/data.json
├─ 5. Verify: Count tasks, check JSON valid
└─ 6. Git commit: "Restored from backup after corruption"

Result: Data recovered, minimal loss (only changes since backup)
```

### Scenario 2: Agent Crashes
```
QUANTA crashes while monitoring

SYSTEMD (auto-detects):
├─ Quanta process died
├─ Restart attempt #1
├─ If fails 5 times in 1 hour → Stop trying
└─ Log: "Quanta crashed, exceeded restart limit"

HELIOS (next audit):
├─ Check: systemctl status quanta
├─ Detect: Service stopped
└─ Report: "Quanta crashed, needs attention"

CHAD_YI:
└─ Notify you: "Quanta crashed 5 times. Check logs or credentials."

YOU: Decide to fix or wait
```

### Scenario 3: Dashboard Breaks
```
Dashboard shows blank page

CHAD_YI:
├─ 1. Check: Did I touch dashboard files? → No
├─ 2. Check: Is DATA/data.json valid? → Yes
├─ 3. Check: Is Render working? → Yes
├─ 4. Conclusion: CSS/JS bug, not data
└─ 5. Fix: Edit dashboard code (safe, doesn't touch data)

Result: Dashboard fixed, data never at risk
```

---

## BACKUP STRATEGY (How We Never Lose Data)

### Layer 1: Git History
```
Every git commit = snapshot
Can see: "What changed between yesterday and today?"
Can revert: "Go back to exactly how it was yesterday"
Stored: On GitHub (remote backup)
```

### Layer 2: Manual Backups
```
BEFORE every change I make:
├─ Create: DATA/backups/manual/data-[timestamp]-[reason].json
├─ Example: data-2026-02-12-2345-PRE-AGENT-CREATE.json
├─ Keep: Forever (until you delete)
└─ Use: When I need to undo a specific change
```

### Layer 3: Auto Backups
```
Every hour (automatic):
├─ Create: DATA/backups/auto/data-[hour].json
├─ Keep: Last 48 hours only
└─ Use: If corruption detected and manual backups confusing
```

### Recovery Commands
```bash
# List available backups
ls -lt DATA/backups/manual/ | head -10

# Restore from specific backup
cp DATA/backups/manual/data-2026-02-12-2345-PRE-...json DATA/data.json

# Verify after restore
python3 scripts/verify-data.py
```

---

## MY STEP-BY-STEP WORKFLOW (How I Build This)

### Phase 1: Foundation (2-3 hours)
```
Step 1: Create directory structure
├─ Create DATA/ directory
├─ Create DATA/backups/auto/
├─ Create DATA/backups/manual/
└─ Create agents/_templates/

Step 2: Move data safely
├─ Copy mission-control-dashboard/data.json → DATA/data.json
├─ Create symlink: dashboard/data.json → ../DATA/data.json
├─ Test: Dashboard still works
└─ If works: Delete original, keep symlink

Step 3: Set up backups
├─ Create scripts/backup-before-change.sh
├─ Create scripts/list-backups.sh
├─ Create scripts/restore.sh
├─ Create scripts/verify-data.sh
└─ Test: Create backup → Restore → Verify

Step 4: Git commit
└─ "Phase 1: Foundation complete, data protected"
```

### Phase 2: Agent Framework (2-3 hours)
```
Step 1: Create agent templates
├─ agents/_templates/new-agent/contract.yaml
├─ agents/_templates/new-agent/MEMORY.md
└─ agents/_templates/new-agent/[folders]

Step 2: Document existing agents
├─ Create agents/chad-yi/contract.yaml
├─ Create agents/helios/contract.yaml
├─ Create agents/quanta/contract.yaml
└─ ... (all agents)

Step 3: Test agent communication
├─ Create test inbox/outbox
├─ Write test status file
├─ Verify Helios can read it
└─ Git commit
```

### Phase 3: Helios Setup (2 hours)
```
Step 1: Install Helios service
├─ Create helios.py (audit script)
├─ Create helios.service
├─ Install: sudo systemctl enable helios
└─ Start: sudo systemctl start helios

Step 2: Configure Helios
├─ Set 15-minute cron
├─ Set up llava model for screenshots
├─ Test audit cycle
└─ Verify reports in outbox

Step 3: Test full loop
├─ Helios audits → Reports → I read → Update data
└─ Git commit
```

### Phase 4: Quanta Activation (2 hours)
```
Step 1: Install Quanta service
├─ Create quanta.service
├─ Install: sudo systemctl enable quanta
└─ Start: sudo systemctl start quanta

Step 2: Configure Quanta
├─ Set up .env file with API keys
├─ Test monitoring (paper trading mode)
└─ Verify outbox reports

Step 3: Test trade flow
├─ Wait for signal (or mock one)
├─ Verify alert appears
├─ Verify dashboard updates
└─ Git commit
```

---

## WHAT YOU NEED TO DO

### Nothing for Phase 1-2
I do everything.

### Phase 3 (Helios): Install Ollama models
```bash
# You run these commands:
ollama pull qwen2.5:7b      # For Helios brain
ollama pull llava:13b       # For Helios eyes (screenshots)
```

### Phase 4 (Quanta): Provide API keys
```
You tell me (securely):
- Telegram API ID
- Telegram API Hash
- OANDA API Key (when ready for live trading)
```

---

## SUCCESS CRITERIA (How We Know It Works)

### Phase 1 Complete When:
- [ ] DATA/data.json exists and is valid
- [ ] Dashboard reads from symlink correctly
- [ ] Backup scripts work (create, list, restore)
- [ ] 72 tasks still present, no data loss

### Phase 2 Complete When:
- [ ] All 6 agents have contract.yaml files
- [ ] Agent template exists for future agents
- [ ] Inbox/outbox structure tested

### Phase 3 Complete When:
- [ ] Helios service running 24/7
- [ ] Helios creates audit reports every 15 min
- [ ] I receive consolidated reports from Helios
- [ ] Dashboard shows Helios status

### Phase 4 Complete When:
- [ ] Quanta service running 24/7
- [ ] Quanta monitors CALLISTOFX
- [ ] Trade alerts appear in outbox
- [ ] Dashboard shows Quanta trades
- [ ] You receive Telegram alerts for trades

---

## RISKS AND MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Symlink breaks dashboard | Medium | High | Test thoroughly before deleting original |
| I corrupt data during move | Low | High | Copy first, test, then delete |
| Helios can't analyze screenshots | Medium | Medium | Fallback to text-only audit |
| Quanta crashes repeatedly | Medium | Medium | Auto-restart with limit, alert you |
| Backup scripts fail silently | Low | High | Verify after each backup |
| Render stops syncing | Low | High | GitHub Pages fallback |

---

## TIMELINE

| Phase | Work | Time | Your Action |
|-------|------|------|-------------|
| 1 | Foundation | 2-3 hrs | None |
| 2 | Agent Framework | 2-3 hrs | None |
| 3 | Helios Setup | 2 hrs | Install 2 Ollama models |
| 4 | Quanta Activation | 2 hrs | Provide API keys |
| **Total** | | **8-10 hrs** | **~30 min of your time** |

---

## APPROVAL

**This architecture:**
- ✅ Separates data from UI (prevents data loss)
- ✅ Backs up automatically (recovery possible)
- ✅ Scales to many agents (template system)
- ✅ Real-time updates (Render 30s refresh)
- ✅ Works on mobile (responsive design)
- ✅ Clear reporting chain (You → Me → Agents → Helios → Me → You)

**Say "BUILD IT" and I start Phase 1 immediately.**
