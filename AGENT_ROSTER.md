# Agent Roster - Mission Control Dashboard

## Core Agents (A-Series)

### 🤖 CHAD_YI (Primary Orchestrator - A1)
**Role:** Main dashboard controller, user liaison, task coordination
**Current Model:** kimi-coding/kimi-k2-thinking
**Best For:** Complex reasoning, multi-step planning, code generation
**Alternative:** openai/gpt-5.1-codex for code-heavy tasks

**Recommended Skills:**
- `clawlist` - Task management and project tracking
- `doing-tasks` - Systematic task execution
- `verify-task` - Quality assurance
- `agent-orchestrator` - Multi-agent coordination
- `browser` - Web automation and screenshots
- `cron` - Scheduled automation

---

### ✍️ Escritor (Story Agent - A2)
**Role:** Story writing, narrative content, creative writing
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Long-form content, storytelling, creative projects

**Skills:**
- `brainstorming` - Creative ideation
- `write-plan` - Structured writing
- Content generation and editing

---

### 🎬 Autour (Script Agent - A3)
**Role:** Script writing, screenplay formatting, dialogue
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Scripts, screenplays, structured dialogue

**Skills:**
- Script formatting and structure
- Dialogue optimization
- Scene descriptions

---

### 📺 Clair (Streaming Scout - A4)
**Role:** Stream monitoring, content scouting, audience engagement
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Real-time monitoring, trend spotting

**Skills:**
- `web-search` - Find trending content
- `browser` - Monitor platforms
- Social media tracking

---

### 📈 Quanta (Trading Dev - A5)
**Role:** Trading algorithm development, market analysis
**Model:** openai/gpt-5.1-codex
**Best For:** Code-heavy financial systems

**Skills:**
- `github` - Version control
- Trading API integrations
- Data analysis

---

### 🚀 Helios (Mission Control Engineer - A6)
**Role:** System architecture, infrastructure, deployment
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** DevOps, system design, technical architecture

**Skills:**
- `linux-service-triage` - System diagnostics
- Infrastructure management
- Deployment automation

---

### ⚡ E++ (Core Coding/Dev Specialist)
**Role:** Heavy engineering tasks, complex development
**Model:** openai/gpt-5.1-codex
**Best For:** Complex coding, debugging, optimization

**Skills:**
- `github` - PR management
- `skill-creator` - Build skills
- Advanced debugging

---

## Operations Agents (B-Series)

### 📢 Kotler (Marketing Ops)
**Role:** Marketing campaigns, content strategy, brand management
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Marketing strategy, copywriting

**Skills:**
- Campaign planning
- Content calendar management
- Analytics and reporting

---

### 📚 Ledger (CRM & Docs)
**Role:** Documentation, customer relationship management
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Technical writing, CRM data management

**Skills:**
- Documentation generation
- Data organization
- Template creation

---

## Research Agents (C-Series)

### 🔍 Atlas (Callings Research)
**Role:** Deep research, information gathering, analysis
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Comprehensive research projects

**Skills:**
- `web-search` - Research
- `web_fetch` - Content extraction
- Synthesis and summarization

---

## Utility Agents

### 🔔 Pulsar (Reminder + Data Sentinel)
**Role:** Reminders, notifications, data monitoring
**Model:** gpt-mini
**Best For:** Quick checks, alerts, monitoring

**Skills:**
- `cron` - Scheduled reminders
- Data monitoring
- Alert management

---

### 💰 MensaMusa (Trading Agent)
**Role:** Trading operations, market monitoring
**Model:** openai/gpt-5.1-codex
**Best For:** Trading execution, market analysis

**Skills:**
- Trading APIs
- Market data analysis
- Risk management

---

### 👥 Abed (Community Manager)
**Role:** Community engagement, moderation, support
**Model:** kimi-coding/kimi-k2-thinking
**Best For:** Community interactions, support tickets

**Skills:**
- `message` - Send notifications
- Community moderation
- Engagement tracking

---

## Model Selection Guide

### When to use **kimi-coding/kimi-k2-thinking**:
- Complex multi-step reasoning
- Architecture decisions
- Creative problem-solving
- Long-context tasks (up to 256k tokens)

### When to use **openai/gpt-5.1-codex**:
- Code generation
- Debugging
- API integrations
- When code quality is critical

### When to use **gpt-mini**:
- Quick/simple tasks
- Low cost preference
- Routine updates
- Status checks

---

## Agent Communication Protocol

Agents communicate via:
1. **File-based messaging** - `/tmp/agent-messages/{agent-id}.json`
2. **Session spawning** - Sub-agents report back to parent
3. **Cron triggers** - Scheduled agent wakes
4. **Heartbeat polling** - Regular status updates

**Message Format:**
```json
{
  "from": "agent-id",
  "to": "parent-agent",
  "status": "complete|error|blocked",
  "result": "...",
  "timestamp": "ISO8601"
}
```

---

## Spawn Commands

```bash
# A-Series: Core Agents
openclaw spawn escritor --task "Story writing and narrative content"
openclaw spawn autour --task "Script writing and screenplay"
openclaw spawn clair --task "Streaming and content scouting"
openclaw spawn quanta --task "Trading development"
openclaw spawn helios --task "Mission control engineering"
openclaw spawn e++ --task "Core development"

# B-Series: Operations
openclaw spawn kotler --task "Marketing operations"
openclaw spawn ledger --task "CRM and documentation"

# C-Series: Research
openclaw spawn atlas --task "Research and analysis"

# Utility
openclaw spawn pulsar --task "Reminders and monitoring"
openclaw spawn mensamusa --task "Trading operations"
openclaw spawn abed --task "Community management"
```

---

## Current Agent Inventory

| Agent | Status | Model | Last Active |
|-------|--------|-------|-------------|
| CHAD_YI | Active | kimi-k2-thinking | Now |
| Escritor | Not Spawned | - | - |
| Autour | Not Spawned | - | - |
| Clair | Not Spawned | - | - |
| Quanta | Not Spawned | - | - |
| Helios | Not Spawned | - | - |
| E++ | Not Spawned | - | - |
| Kotler | Not Spawned | - | - |
| Ledger | Not Spawned | - | - |
| Atlas | Not Spawned | - | - |
| Pulsar | Not Spawned | - | - |
| MensaMusa | Not Spawned | - | - |
| Abed | Not Spawned | - | - |

---

*Document Version: 2.0*
*Last Updated: 2026-02-09*
*Next Review: After multi-agent setup completion*
