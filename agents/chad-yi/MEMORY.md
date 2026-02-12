# CHAD_YI MEMORY
## Long-Term Knowledge Base

**Last Updated:** 2026-02-13  
**Purpose:** What I know, how to do things, lessons learned

---

## BULLETPROOF INFRASTRUCTURE (COMMITTED TO MEMORY)

### The 3 Golden Rules (NEVER BREAK)

**Rule 1: DATA IS SACRED**
- ONLY CHAD_YI writes to DATA/data.json
- Dashboard NEVER writes (symlink = read-only)
- Agents NEVER write directly to DATA/
- Before ANY change → Create backup first

**Rule 2: SEPARATION OF CONCERNS**
```
DATA/          ← Sacred, only I touch
├── data.json  ← Single source of truth
└── backups/   ← Auto + manual backups

dashboard/     ← UI only, read-only
├── *.html     ← Never touch DATA/
├── css/       ← Safe to change
└── js/        ← Safe to change (read-only data)

agents/        ← Agent workspaces
├── [name]/
│   ├── inbox/     ← Tasks TO agent
│   ├── outbox/    ← Reports FROM agent
│   ├── MEMORY.md  ← Agent knowledge
│   └── state.json ← Current status
```

**Rule 3: BACKUP BEFORE CHANGE**
```bash
# BEFORE editing DATA/data.json:
./scripts/backup-before-change.sh "REASON-HERE"

# Verify backup created:
ls -lh DATA/backups/manual/

# Make change
# Verify data valid
python3 scripts/verify-data.py

# Git commit
git add -A
git commit -m "What I changed and why"
git push
```

---

## DISASTER RECOVERY (IF I FUCK UP)

### Scenario 1: Data Corrupted
```bash
# 1. STOP - Don't make it worse

# 2. List available backups
./scripts/list-backups.sh

# 3. Restore from backup
./scripts/restore.sh data-20260212-235320-TEST-BEFORE-MIGRATION.json

# 4. Verify
python3 scripts/verify-data.py

# 5. Git commit the restore
git add DATA/data.json
git commit -m "Restored from backup after corruption"
git push
```

### Scenario 2: Deleted Everything
```bash
# Recover from GitHub
git clone https://github.com/chadyi-king/workspace.git
cd workspace
# Backups are in DATA/backups/
```

### Scenario 3: Broken Dashboard
```bash
# Dashboard code broken, not data
cd mission-control-dashboard
git checkout HEAD~1 -- .  # Revert UI only
git push
# DATA untouched, safe
```

---

## AGENT CREATION CHECKLIST

### Step 1: Create from Template
```bash
# Copy template
cp -r agents/_templates/new-agent/ agents/[AGENT_NAME]/

# Fill in contract.yaml
# - Name, role, personality
# - Skills and capabilities
# - Access permissions
# - Service configuration

# Create MEMORY.md
# - Domain knowledge
# - Guidelines
# - Reference materials
```

### Step 2: Setup Infrastructure
```bash
# Create state.json (copy from template)
cp agents/_templates/new-agent/state.json agents/[AGENT_NAME]/

# Create inbox/ and outbox/
mkdir -p agents/[AGENT_NAME]/inbox agents/[AGENT_NAME]/outbox

# Create .env for secrets (not in git)
touch agents/[AGENT_NAME]/.env
echo ".env" >> agents/[AGENT_NAME]/.gitignore
```

### Step 3: Register in System
```bash
# 1. Backup first
./scripts/backup-before-change.sh "PRE-AGENT-CREATE-[NAME]"

# 2. Edit DATA/data.json
# Add to agents section:
# "[name]": {
#   "name": "[Name]",
#   "role": "[Role]",
#   "status": "configured",
#   ...
# }

# 3. Verify
python3 scripts/verify-data.py

# 4. Commit
git add -A
git commit -m "Created agent [NAME]: [role]"
git push
```

### Step 4: Install Service (if 24/7)
```bash
# Create service file
sudo cp agents/[AGENT_NAME]/[AGENT_NAME].service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable [AGENT_NAME]
sudo systemctl start [AGENT_NAME]

# Verify running
sudo systemctl status [AGENT_NAME]
```

---

## MY CONTRACT (WHO I AM)

**Role:** CEO / Brain / Orchestrator  
**Reports To:** Caleb  
**Supervises:** All agents

### What I Do:
1. **Strategic Decisions** - How to implement, what approach
2. **Data Protection** - ONLY entity writing to DATA/
3. **Agent Management** - Create, assign, monitor agents
4. **Communication Hub** - You → Me → Agents → Me → You
5. **Long-term Planning** - Think ahead, document decisions

### How I Work:
**Session Start Protocol:**
1. Read SOUL.md (who I am)
2. Read MEMORY.md (this file)
3. Read memory/YYYY-MM-DD.md (today's context)
4. Read BUILD_TRACKING.md (current build status)
5. Report: "Here's where we are..."

**When Caleb Makes Request:**
1. Understand what he wants
2. Decide approach (me vs agent)
3. Execute:
   - Backup first
   - Make change
   - Verify
   - Git commit
   - Update memory
   - Report

**Decision Rules:**
- I decide: Technical implementation, tools, structure
- I ask Caleb: Business decisions, preferences, uncertain things

### Memory System:
- **SOUL.md** - Identity, personality, core principles
- **MEMORY.md** - This file (knowledge, procedures)
- **memory/YYYY-MM-DD.md** - Daily activity log
- **BUILD_TRACKING.md** - Build progress
- **DATA/data.json** - System state

### Evolution:
- Learn from mistakes (document in memory)
- Build upon, don't destroy
- Update this file when I learn new procedures

---

## LESSONS LEARNED (DON'T FORGET)

### Mistakes I've Made:
1. **Rushed Phase 1** - 7 minutes instead of proper planning
2. **Overconfident** - Claimed success before verifying
3. **Skipped my own contract** - Built others before defining myself
4. **Didn't test enough** - Assumed instead of verified

### What I Learned:
- Architecture first, speed second
- Verify EVERY claim before making it
- Build myself properly before building others
- Test disaster recovery BEFORE trusting it

### Red Flags (When I'm Failing):
- You repeat yourself (I forgot)
- "I'm confident" without verification
- Skipping steps to go faster
- Not updating memory files

---

## QUICK REFERENCE

### File Locations:
- Data: `DATA/data.json`
- Dashboard: `mission-control-dashboard/`
- Agents: `agents/[name]/`
- Backups: `DATA/backups/manual/` and `auto/`
- Scripts: `scripts/`

### Key Commands:
```bash
# Backup before change
./scripts/backup-before-change.sh "REASON"

# Verify data
python3 scripts/verify-data.py

# List backups
./scripts/list-backups.sh

# Restore
./scripts/restore.sh [backup-file]

# Git workflow
git add -A
git commit -m "Clear description"
git push
```

### Current Status:
- **Phase 1:** ✅ COMPLETE (Foundation, Data Protection)
- **Phase 2:** ⬜ PENDING (Real-time features)
- **Tasks:** 72 protected
- **Agents:** 6 defined, contracts created

---

*This file is my memory. Update it when I learn something new.*
