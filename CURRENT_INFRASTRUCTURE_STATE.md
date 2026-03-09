# CURRENT_INFRASTRUCTURE_STATE.md

_Last grounded: 2026-03-10 02:4x SGT_

This file is the current human-readable bridge between:
- the **actual live system**
- the **intended agent architecture**
- the **known gaps** still blocking consolidation

---

## 1. Canonical roles

### System-wide rule
- Every agent, including CHAD_YI, should have ACP capability in the final architecture.

### CHAD_YI = The Face
- human-facing interface
- receives Caleb's instructions
- coordinates work
- does quick ops, edits, reporting, escalation
- should not pretend to be the deep architecture center

### Cerebronn = The Brain
- deep planning / architecture / heavy coding
- works through files and structured handoff
- should produce executable plans and real builds

### Helios = The Spine / Auditor
- should run on a free local model (for example Qwen 3.5 via Ollama)
- audits/pokes all agents every 15 minutes
- checks what is actually running
- audits agents and truth surfaces
- detects drift between dashboard, files, and runtime
- reports issues to CHAD_YI
- pokes the system to keep it honest

### Specialists
- Quanta = trading
- Forger = website building / coding specialist
- other specialists operate under the Face / Brain / Spine structure, not as separate top-level architecture centers

---

## 2. Current live state (verified)

Verified from live infra audit on 2026-03-10:
- `openclaw-gateway` active
- `helios` active
- `cerebronn` active
- `forger` active
- old junk services OFF: `mc-websocket`, `gws-agent`, old `quanta`, `chad-report-delivery`
- Quanta v3 process running
- Quanta heartbeat fresh
- live dashboard reachable
- `ACTIVE.md` fresh enough for heartbeat policy

This means the runtime is not conceptually dead. It is alive, but the documentation / truth surfaces are still messy.

---

## 3. Actual truth surfaces right now

### Operational truth
- `~/.openclaw/agents/` = active agent system
- OpenClaw gateway + running services = live execution layer

### Human / dashboard truth
- `ACTIVE.md` = declared source of truth for dashboard tasks
- operative dashboard JSON path = `mission-control-dashboard/data.json`
- live dashboard = `https://red-sun-mission-control.onrender.com`
- pinned messages = authoritative dashboard reference context when Caleb refers to "the main dashboard"

### Business / continuity truth
- `MEMORY.md`
- `memory/YYYY-MM-DD.md`

---

## 4. Proven mess that still exists

### A. Top-level markdown graveyard
There are too many old architecture / infra / plan docs at the workspace root.
Some are still useful for forensics, but many are stale or contradictory.

Important correction:
- `UNIFIED_ARCHITECTURE_PROPOSAL.md` is a main architecture document Caleb expects to be read for understanding.
- It should stay in the canonical read path, not be treated as junk.

### B. Conflicting role docs
At least one older file (`CHAD_YI_AND_HELIOS_ROLES.md`) conflicts with the current Face/Brain split by describing CHAD_YI as "The Brain".
That file is historical, not canonical.

### C. Multiple `data.json` surfaces
These are not the same file and do not currently match:
- `/home/chad-yi/.openclaw/workspace/data.json`
- `/home/chad-yi/.openclaw/workspace/DATA/data.json`
- `/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json`

Current best read of reality:
- `mission-control-dashboard/data.json` is the **operative live dashboard path** used by Helios state, audits, and dashboard update scripts
- root `data.json` and `DATA/data.json` are **legacy/confusing surfaces** until explicitly consolidated

This is still a reverse-engineering problem because old docs and old scripts refer to different JSON paths.

### D. Incomplete consolidation
Still unresolved:
- duplicate `mission-control-workspace` topology
- one official Quanta control/service path
- one fully canonical dashboard data path
- full collapse of stale top-level docs into a single canonical architecture story

---

## 5. Working interpretation of the 3 phases Caleb wants

### Phase 1 — Cleanup
Archive or remove noncanonical clutter so old junk stops polluting understanding.

### Phase 2 — Reverse engineer reality
Starting from the dashboard and live services, determine:
- what is actually running
- what file paths are actually used
- what the current architecture really is
- where it diverges from the intended design

### Phase 3 — Link and fix
Unify surviving truth surfaces and make the architecture cohere:
- one canonical agent structure
- one canonical dashboard data path
- one canonical explanation file
- less drift between runtime, files, and reporting

---

## 6. Current best canonical read order

1. `SOUL.md`
2. `IDENTITY.md`
3. `USER.md`
4. `MEMORY.md`
5. `memory/YYYY-MM-DD.md` (today + yesterday)
6. `CURRENT_INFRASTRUCTURE_STATE.md`
7. `CANONICAL_READSET.md`
8. `ACTIVE.md`
9. `HEARTBEAT.md`
10. `~/.openclaw/openclaw.json`

---

## 7. Immediate next fixes

1. archive obviously stale/conflicting top-level docs
2. update `CANONICAL_READSET.md` so future sessions stop reading conflicting files first
3. trace which `data.json` path is actually authoritative for the live dashboard pipeline
4. choose one canonical dashboard data path and re-point everything else to it

This file is not the final architecture document.
It is the grounded bridge from messy current reality to a clean final structure.
