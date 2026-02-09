# Token-Efficient Agent Memory Architecture

## Problem: Token Usage
- Full context = expensive
- Agents loading everything = token blowup
- Need: Focused, minimal, relevant memories only

## Solution: Hierarchical Memory System

### Level 1: CHAD_YI (You - The Brain)
- Full access to all memories
- Decides what agents need to know
- Acts as "memory router"

### Level 2: Agent-Specific Memories
Agents only load:
1. Their SOUL.md (who they are)
2. Their TASK.md (current assignment only)
3. Relevant project files (not everything)

### Level 3: Shared Context
Agents share via:
- File-based handoffs (not chat context)
- Summarized reports (not full transcripts)
- Task completion signals

---

## Memory Files Structure

### For Escritor (Story Agent)
```
agents/escritor/
├── SOUL.md          # Who he is (minimal, ~200 tokens)
├── MEMORY.md        # His experiences only
├── task-current.md  # Current assignment
└── handoff/         # Files from CHAD_YI
    ├── brief-001.md
    ├── feedback-001.md
    └── context-*.md
```

### For Autour (Script Agent)
```
agents/autour/
├── SOUL.md          # Who he is (minimal, ~200 tokens)
├── MEMORY.md        # His experiences only
├── task-current.md  # Current assignment
└── handoff/         # Files from CHAD_YI
    ├── brief-001.md
    ├── feedback-001.md
    └── context-*.md
```

---

## Token Budget Per Agent

| Component | Token Budget | Purpose |
|-----------|--------------|---------|
| SOUL.md | ~200 | Personality & role |
| TASK.md | ~300 | Current assignment |
| Context Files | ~500-1000 | Relevant project data |
| **TOTAL** | **~1000-1500** | Per task session |

Compare to: Full context = 10,000+ tokens

**Savings: 85-90% token reduction**

---

## How It Works

### 1. Task Delegation (CHAD_YI → Agent)
```
CHAD_YI creates:
- task-brief.md (what to do)
- context-relevant.md (only needed files)
- constraints.md (budget, style, format)

Saves to: agents/{agent}/handoff/
```

### 2. Agent Works (Isolated)
```
Agent loads:
- SOUL.md (who am I)
- TASK.md (what to do)
- handoff/ files (context)

Agent does NOT load:
- Full workspace
- Other agent memories
- Unrelated projects
```

### 3. Agent Reports Back (Agent → CHAD_YI)
```
Agent creates:
- result-summary.md (concise output)
- deliverables/ (files created)
- next-steps.md (if needed)

CHAD_YI reviews, integrates, updates main MEMORY.md
```

---

## Memory Isolation Rules

### Agents CANNOT:
- Access each other's memories
- Load full workspace context
- Auto-search all files
- Keep unlimited history

### Agents CAN:
- Read files in their handoff/ folder
- Write to their deliverables/ folder
- Request specific files from CHAD_YI
- Report back with summaries

---

## BotFather Setup (Still Required)

Yes, you still need to:
1. Message @BotFather
2. Create @EscritorBot and @AutourBot
3. Get tokens (already have these)
4. Set bot descriptions

But the **integration** is what I handle:
- Routing messages
- Delegating tasks
- Managing context
- Summarizing responses

---

## Re:Unite Story Handoff

Your story is already organized:
- `/projects/A2-reunite/resources/ReUnite-Story-Bible-Final.md`
- `/projects/A2-reunite/resources/ReUnite-Chapters.md`

When Escritor needs it, I'll pass:
- Summary only (~500 tokens)
- Not the full bible (~3000+ tokens)
- Key characters, plot points, style notes

---

## Implementation Plan

### Step 1: Create Agent Identities
- [ ] Escritor SOUL.md
- [ ] Autour SOUL.md
- [ ] Memory architecture

### Step 2: BotFather Setup
- [ ] You verify @EscritorBot
- [ ] You verify @AutourBot
- [ ] Test basic messaging

### Step 3: Integration
- [ ] Add bot configs to OpenClaw
- [ ] Set up delegation routing
- [ ] Test task handoff

### Step 4: First Task
- [ ] Delegate Re:Unite chapter to Escritor
- [ ] Monitor token usage
- [ ] Refine process

---

## Token Usage Estimates

| Scenario | Without System | With System | Savings |
|----------|---------------|-------------|---------|
| Story task | 8,000 tokens | 1,200 tokens | 85% |
| Script task | 10,000 tokens | 1,500 tokens | 85% |
| Research task | 6,000 tokens | 1,000 tokens | 83% |

**Monthly savings: ~$50-100 in API costs**

---

Ready to proceed with Step 1 (creating SOUL.md files)?