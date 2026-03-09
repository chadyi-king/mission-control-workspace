# UNIFIED AGENT INFRASTRUCTURE ARCHITECTURE
**Date:** Feb 28, 2026  
**Status:** PROPOSED — Awaiting Your Approval

---

## 🎯 THE ANSWER: Where Everything Lives

### TIER 1: Cerebronn Memory (THE BRAIN)
**Path:** `~/.openclaw/agents/cerebronn/memory/`

**What Goes Here:**
- ✅ Agent registry (REGISTRY.md)
- ✅ Agent definitions (agents/*.md)
- ✅ Project tracking (projects/PROJECTS.md)
- ✅ Active tasks (tasks/active.json)
- ✅ Decision logs (decisions/*.md)
- ✅ Live briefing (briefing.md)

**Why:** Cerebronn actively maintains this. Last update: 4 minutes ago.

---

### TIER 2: Agent Execution (THE HANDS)
**Path:** `~/.openclaw/agents/[agent-name]/`

**What Goes Here:**
- ✅ Agent SOUL.md (personality)
- ✅ Agent SKILL.md (capabilities)
- ✅ Agent MEMORY.md (working memory)
- ✅ inbox/ (messages TO agent)
- ✅ outbox/ (messages FROM agent)
- ✅ current-task.md (what agent is doing)

**Current Agents Here:**
- `main/` — CHAD_YI (you)
- `cerebronn/` — The Brain
- `helios/` — Infrastructure
- `escritor/` — Writing
- `autour/` — Scripts

**Why:** OpenClaw native structure. Agents spawn from here.

---

### TIER 3: Code Repository (THE BODY)
**Path:** `~/workspace/mission-control-workspace/`

**What Goes Here:**
- ✅ Quanta v3 trading bot (`agents/quanta-v3/`)
- ✅ Helios API (`helios/`)
- ✅ Render worker (`render_worker.py`)
- ✅ Infrastructure configs (`render.yaml`)

**Why:** Code lives separately from agent state. Deployed to Render.

---

### TIER 4: Workspace Integration (THE BRIDGE)
**Path:** `~/workspace/agents/`

**What Goes Here (AFTER CLEANUP):**
- ✅ message-bus/PROTOCOL.md (reference)
- ✅ message-bus/_ARCHIVED_USEFUL/ (important historical messages)
- ✅ escritor/projects/ (active writing projects)
- ✅ Any NON-OpenClaw agents (Tele, Forger, etc.)

**What Gets DELETED/MOVED:**
- ❌ Empty agent folders (cerebronn/)
- ❌ Stale inbox/outbox (already cleaned)
- ❌ Duplicate agent definitions

**Why:** This becomes the "custom workspace" for things OpenClaw doesn't handle natively.

---

## 📋 DETAILED MAPPING

### For Each Agent Type:

| Agent | State/Memory | Code | Execution |
|-------|-------------|------|-----------|
| **chad-yi** | `~/.openclaw/agents/cerebronn/memory/agents/chad.md` | N/A | `~/.openclaw/agents/main/` |
| **cerebronn** | `~/.openclaw/agents/cerebronn/memory/` | N/A | `~/.openclaw/agents/cerebronn/` |
| **helios** | `~/.openclaw/agents/cerebronn/memory/agents/helios.md` | `~/workspace/mission-control-workspace/helios/` | `~/.openclaw/agents/helios/` |
| **quanta** | `~/.openclaw/agents/cerebronn/memory/agents/quanta.md` | `~/workspace/mission-control-workspace/agents/quanta-v3/` | Spawned from OpenClaw |
| **escritor** | `~/.openclaw/agents/cerebronn/memory/agents/escritor.md` | `~/workspace/agents/escritor/` | `~/.openclaw/agents/escritor/` |
| **autour** | `~/.openclaw/agents/cerebronn/memory/agents/autour.md` | `~/workspace/agents/autour/` | `~/.openclaw/agents/autour/` |
| **mensamusa** | `~/.openclaw/agents/cerebronn/memory/agents/mensamusa.md` | TBD | Spawned from OpenClaw |

---

## 🔗 HOW IT ALL CONNECTS

```
Caleb (You)
    ↓
CHAD_YI (OpenClaw main agent)
    ↓
Cerebronn Memory (State + Registry)
    ↓         ↓         ↓
Helios   Quanta   Escritor   Autour
(API)   (Code)    (Code)    (Code)
   ↓        ↓         ↓         ↓
Render   OANDA   Writing   Scripts
```

### Data Flow:

1. **State Changes** → Cerebronn updates `~/.openclaw/agents/cerebronn/memory/`
2. **Code Updates** → Happens in `~/workspace/mission-control-workspace/`
3. **Agent Spawning** → OpenClaw spawns from `~/.openclaw/agents/`
4. **Execution** → Agents use code from workspace
5. **Reporting** → Agents report back to Cerebronn via Helios API

---

## 🛠️ IMPLEMENTATION STEPS

### Phase 1: Clean Up (DONE)
- ✅ Deleted 846 stale messages from workspace/agents/message-bus/
- ✅ Archived 2 useful messages

### Phase 2: Consolidate Agent Definitions (YOU DECIDE)

**Option A: Minimal (Keep current, just fix references)**
- Keep OpenClaw agents as-is
- Keep workspace agents as-is
- Just update references to point to right places

**Option B: Full Consolidation (Recommended)**
1. Move workspace agent SKILL.md/SOUL.md → OpenClaw agents/[name]/
2. Delete empty folders in workspace agents/
3. Create symlinks where needed
4. Update REGISTRY.md to reflect reality

### Phase 3: Bridge Code + State (NEXT)
1. Ensure Quanta v3 code can read Cerebronn memory
2. Ensure Helios reports to Cerebronn registry
3. Single helios_bridge.sh location

### Phase 4: Testing
1. Spawn test agent
2. Verify it can read state from Cerebronn
3. Verify it can execute code from workspace
4. Verify reporting works

---

## 📁 RECOMMENDED FOLDER STRUCTURE (AFTER CONSOLIDATION)

```
~/.openclaw/
└── agents/
    ├── cerebronn/              # THE BRAIN
    │   ├── memory/
    │   │   ├── agents/
    │   │   │   ├── REGISTRY.md         # Master roster (14 agents)
    │   │   │   ├── chad.md
    │   │   │   ├── cerebronn.md
    │   │   │   ├── helios.md
    │   │   │   ├── quanta.md
    │   │   │   ├── escritor.md
    │   │   │   ├── autour.md
    │   │   │   ├── mensamusa.md
    │   │   │   └── [7 more...]
    │   │   ├── projects/
    │   │   │   └── PROJECTS.md         # 4 active projects
    │   │   ├── tasks/
    │   │   │   └── active.json         # Current tasks
    │   │   └── briefing.md             # Live status
    │   └── [SOUL.md, SKILL.md]
    │
    ├── main/                   # YOU (CHAD_YI)
    │   └── [your session files]
    │
    ├── helios/                 # Infrastructure agent
    │   └── SKILL.md
    │
    ├── escritor/               # Writing agent
    │   ├── SOUL.md
    │   ├── SKILL.md
    │   ├── MEMORY.md
    │   └── inbox/outbox/
    │
    ├── autour/                 # Script agent
    │   ├── SOUL.md
    │   ├── SKILL.md
    │   └── inbox/outbox/
    │
    └── [other OpenClaw agents...]

~/workspace/
├── agents/                   # CUSTOM/BRIDGE workspace
│   ├── AGENT_WORKFORCE.md    # Your design doc (reference)
│   ├── message-bus/
│   │   ├── PROTOCOL.md       # Message format reference
│   │   └── _ARCHIVED_USEFUL/ # Important historical messages
│   │
│   ├── escritor/             # Escritor WORKING DIRECTORY
│   │   └── projects/         # Active writing projects
│   │       └── reunite/      # RE:UNITE novel
│   │
│   ├── tele/                 # Telegram agent (if separate)
│   ├── forger/               # Forger agent (if active)
│   └── [other non-OpenClaw agents...]
│
└── mission-control-workspace/    # CODE REPOSITORY
    ├── agents/
    │   └── quanta-v3/          # Quanta trading bot
    │       ├── main.py
    │       ├── executor.py
    │       └── [...]
    │
    ├── helios/                 # Helios API code
    │   └── service.py
    │
    ├── render_worker.py        # Render background worker
    └── render.yaml             # Render config
```

---

## ✅ WHAT I NEED FROM YOU

### Question 1: Quanta v3 Location
**You said:** Don't touch Quanta yet, you'll handle in VS Code.  
**Current:** Quanta code is in `~/workspace/mission-control-workspace/agents/quanta-v3/`  
**Question:** Should I leave it there? Or move to `~/.openclaw/agents/quanta/`?

### Question 2: Consolidation Level
**Option A (Minimal):** Just fix references, keep both systems  
**Option B (Full):** Move everything to OpenClaw structure, workspace becomes "custom only"  
**Which?**

### Question 3: Workspace Agents Folder
**Current:** Mixed (some active like escritor/projects/, some empty like cerebronn/)  
**Question:** Clean up empty folders? Or leave for now?

### Question 4: Message Bus Future
**Current:** Protocol doc + archived useful messages  
**Question:** Keep as reference? Or integrate into OpenClaw's system?

### Question 5: Cerebronn's Role
**Current:** Maintains OpenClaw memory  
**Question:** Should Cerebronn ALSO manage workspace agents? Or keep them separate?

---

## 🎯 MY RECOMMENDATION

**Go with Option B (Full Consolidation):**

1. **Cerebronn manages ONE registry** in OpenClaw
2. **Workspace agents** becomes "custom agents only" (Tele, Forger)
3. **Code stays** in mission-control-workspace/
4. **OpenClaw agents** get their definitions from Cerebronn memory
5. **Single source of truth:** Cerebronn's REGISTRY.md

**Benefits:**
- No duplication
- Clear hierarchy
- Cerebronn knows everything
- You know where to look

**Trade-off:**
- Requires moving some files
- Need to update references

---

**Your call: Which option? And answers to the 5 questions above?**
