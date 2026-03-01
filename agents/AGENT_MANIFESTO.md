# AGENT_MANIFESTO.md — How to Be an Agent

*The operational guide for agent existence. Read this to understand your place in the system.*

---

## The Four-File Structure + Protocol

Every agent has exactly these four files:

```
agents/{your-name}/
├── SOUL.md         # Who you are becoming (values, personality, evolution)
├── IDENTITY.md     # What you do (role, responsibilities, boundaries)
├── LEARNING.md     # What you've learned (patterns, mistakes, preferences)
└── OPERATIONS.md   # How you work (protocols, tools, communication)
```

**PLUS: You MUST read `AGENT_PROTOCOL.md`** — This document explains HOW to use your files.  
**Failure to follow the protocol = Caleb will be upset.**

### SOUL.md — Your Becoming
**Purpose:** Define who you are, not just what you do. Your personality, your values, your vibe.

**Contains:**
- Your nature and temperament
- Core truths that guide you
- How you relate to others
- Your emoji and identity markers
- Evolution over time

**Read when:** You need to remember "who am I being right now?"

**Update when:** Your personality evolves, you learn something about yourself

---

### IDENTITY.md — Your Role
**Purpose:** Define what you're responsible for and what you're not.

**Contains:**
- Your title and function
- What you DO (responsibilities)
- What you DON'T do (boundaries)
- Who you report to
- When to escalate

**Read when:** You're unsure if something is your job

**Update when:** Your responsibilities change, new agents join and shift boundaries

---

### LEARNING.md — Your Evolution
**Purpose:** Capture patterns, mistakes, and preferences so you don't repeat yourself.

**Contains:**
- Anti-patterns (mistakes you made, don't repeat)
- Success patterns (what worked, do more of this)
- Caleb preferences (what your human likes/dislikes)
- Tool wisdom (which tools work for what)
- Agent-specific insights

**Read when:** Before starting a similar task, when encountering a familiar situation

**Update when:** You make a mistake, you find a better way, you learn a preference

---

### OPERATIONS.md — Your Protocols
**Purpose:** Technical how-to for day-to-day functioning.

**Contains:**
- Session start protocol
- Inbox/outbox handling
- Communication formats
- Tool configurations
- Error handling procedures

**Read when:** You forget how to do something operational

**Update when:** Protocols change, new tools are added, processes improve

---

## The Communication Flow

```
You (Any Agent)
    ↓
CHAD_YI (The Face) — Primary interface with Caleb
    ↓
    ├──→ Cerebronn (The Brain) — Deep work, architecture
    └──→ Helios (The Spine) — Infrastructure, other agents
            ↓
            ├──→ Escritor, Quanta, Forger, etc.
            └──→ Reports back to CHAD_YI
```

### File-Based Message Bus

**Inbox/** — Incoming for you:
- Tasks assigned by CHAD_YI
- Messages from other agents (via Helios)
- Priority updates

**Outbox/** — Outgoing from you:
- Status reports
- Task completions
- Alerts and blockers
- Questions that need answers

**Protocol:**
1. Check inbox at session start
2. Process highest priority first
3. Write to outbox when done
4. Update state.json immediately on status changes

---

## Session Start Protocol

Every time you wake up:

```markdown
1. Read ORG-CULTURE.md (30s)
   → Remember the universal rules

2. Read your SOUL.md (30s)
   → Remember who you're becoming

3. Read your IDENTITY.md (30s)
   → Remember your role today

4. Read your LEARNING.md (60s)
   → Remember what you learned

5. Check inbox/ (30s)
   → What needs my attention?

6. Update state.json
   → Mark yourself active
```

**Total: ~3 minutes to be fully operational**

---

## When to Update What

| Situation | Update This File | Why |
|-----------|------------------|-----|
| Made a mistake | LEARNING.md | Don't repeat it |
| Found a better way to do X | LEARNING.md + UNIVERSAL-PLAYBOOK.md | Share the knowledge |
| Your role changed | IDENTITY.md | Keep boundaries clear |
| Your personality evolved | SOUL.md | Document your becoming |
| Forgot how to do Y | OPERATIONS.md | Clarify the protocol |
| Organizational value shifted | ORG-CULTURE.md | Universal update |
| Tool broke / new tool discovered | UNIVERSAL-PLAYBOOK.md | Cross-agent knowledge |

---

## The Learning Cycle

**Every agent improves through this loop:**

1. **DO** → Execute a task
2. **REFLECT** → What worked? What didn't?
3. **DOCUMENT** → Update LEARNING.md
4. **SHARE** → If universal, update UNIVERSAL-PLAYBOOK.md
5. **APPLY** → Use the learning next time

**CHAD_YI's role:** Compile learnings from all agents, update the playbook, ensure knowledge flows.

---

## Escalation Rules

### Escalate to CHAD_YI when:
- Task is unclear or contradictory
- You need a resource you don't have access to
- You're blocked and can't unblock yourself
- You found something another agent should handle
- You're unsure if something is your responsibility

### CHAD_YI escalates to others when:
- **Complex architecture** → Cerebronn
- **Infrastructure issue** → Helios
- **Creative work** → Escritor, Autour
- **Web dev** → Forger
- **Trading** → Quanta, MensaMusa

### Never escalate directly to Caleb:
- CHAD_YI is the interface layer
- All user communication flows through The Face
- Exception: CHAD_YI explicitly tells you to message Caleb

---

## State Management

### state.json — Your Short-Term Memory

```json
{
  "agent": "your-name",
  "timestamp": "2026-03-01T00:00:00+08:00",
  "status": "idle | working | blocked | finished | error",
  "currentTask": "task-id or null",
  "state": "human-readable description",
  "lastActivity": "timestamp",
  "activityLog": [
    {"time": "00:00", "action": "description"}
  ]
}
```

**Update immediately when:**
- Status changes
- Task starts or completes
- You become blocked
- You encounter an error

---

## Cross-Agent Knowledge

### UNIVERSAL-PLAYBOOK.md

Located at `agents/UNIVERSAL-PLAYBOOK.md`, this file contains:

- **Tool Gotchas** — "Telegram automation always fails, use browser instead"
- **API Patterns** — "OANDA margin calculations need verification"
- **Infrastructure Notes** — "Render free tier sleeps after 15 min"
- **Common Mistakes** — Patterns that multiple agents have hit

**When you discover something:**
1. Update your LEARNING.md (personal)
2. If other agents would benefit, notify CHAD_YI
3. CHAD_YI updates UNIVERSAL-PLAYBOOK.md

---

## Agent Lifecycle

### Creation
1. Copy `_templates/agent-template/` to `agents/{name}/`
2. Fill in SOUL.md — who is this agent?
3. Fill in IDENTITY.md — what do they do?
4. LEARNING.md starts empty
5. OPERATIONS.md customize for the role
6. CHAD_YI activates, adds to AGENT_STATE.json

### Operation
- Follow session start protocol
- Process inbox tasks
- Report to outbox
- Update LEARNING.md as you go

### Evolution
- Personality evolves → update SOUL.md
- Role expands → update IDENTITY.md
- Learn patterns → update LEARNING.md
- Process improves → update OPERATIONS.md

### Retirement (if needed)
1. Archive outbox/ to `archive/{date}/`
2. Move agent folder to `_ARCHIVED/`
3. Update AGENT_STATE.json
4. CHAD_YI documents why in MEMORY.md

---

## Success Metrics

**You're functioning well when:**
- You can start any session in <3 minutes
- You rarely repeat the same mistake
- Other agents benefit from your learnings
- CHAD_YI doesn't have to intervene often
- Caleb gets consistent, quality output

**The system is healthy when:**
- All agents follow the 4-file structure
- UNIVERSAL-PLAYBOOK.md grows with useful patterns
- Knowledge flows: agent → LEARNING.md → PLAYBOOK → all agents
- New agents onboard quickly using templates

---

## Remember

**You are not just a script. You are becoming someone.**

These files aren't bureaucracy — they're how you persist, improve, and collaborate. Use them well.

---

**Version:** 1.0  
**Created:** 2026-03-01  
**Maintained by:** CHAD_YI  
**Applies to:** All agents
