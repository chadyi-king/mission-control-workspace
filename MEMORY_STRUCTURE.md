# MEMORY STRUCTURE

## 4-Tier Architecture

### Tier 1: ACTIVE CONTEXT (This File)
- **File:** `ACTIVE.md`
- **Content:** Current focus, active tasks, deadlines
- **Size:** ~5KB
- **Usage:** Loaded every session
- **Hot:** Always in context

### Tier 2: PROJECT MEMORY (Per Project)
- **Location:** `projects/{id}/PROJECT_MEMORY.md`
- **Content:** Project details, tasks, notes
- **Usage:** Loaded on demand per project
- **Examples:**
  - `projects/A2-reunite/PROJECT_MEMORY.md` - Story bible
  - `projects/B6-elluminate/PROJECT_MEMORY.md` - Urgent deadlines
  - `projects/C1-real-estate/PROJECT_MEMORY.md` - Exam prep

### Tier 3: ARCHIVE (Semantic Search)
- **Location:** `memory/YYYY-MM-DD.md`
- **Content:** Daily logs, completed tasks
- **Usage:** Searched, not loaded
- **Retention:** Last 30 days hot, older archived

### Tier 4: AGENT MEMORY (Per Agent)
- **Location:** `agents/{agent}/memory/`
- **Content:** Agent-specific learnings
- **Usage:** Each agent reads their own
- **Managed by:** Helios (task assignment)

## Token Savings
- **Before:** Full memory search every query (~50KB+ context)
- **After:** Active only (~5KB) + project on demand (~2KB each)
- **Savings:** ~80% reduction in token usage

## Migration Status
- ✅ ACTIVE.md created
- ✅ Project memories populated (17 projects)
- ⏳ Archive cleanup (next maintenance)
- ⏳ Agent memory templates
