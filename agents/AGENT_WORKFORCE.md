# Agent Workforce System

## Overview
File-based multi-agent architecture where each agent has:
- Independent memory
- Specialized skills
- Project folders
- Message inbox/outbox
- Task tracking

## Agent Roster (12 Agents)

### A-Series: Core Agents
- **CHAD_YI** (A1) - Orchestrator - YOU
- **Escritor** (A2) - Story Agent
- **Autour** (A3) - Script Agent
- **Clair** (A4) - Streaming Scout
- **Quanta** (A5) - Trading Dev
- **Helios** (A6) - Mission Control Engineer

### Utility Agents
- **E++** - Core Dev Specialist
- **Kotler** - Marketing Ops
- **Ledger** - CRM & Docs
- **Atlas** - Callings Research
- **Pulsar** - Data Sentinel
- **MensaMusa** - Trading Agent
- **Abed** - Community Manager

## Directory Structure

```
/agents/
├── AGENT_ROSTER.md              # This file
├── message-bus/                 # Inter-agent communication
│   ├── pending/                 # Unread messages
│   ├── archive/                 # Processed messages
│   └── templates/               # Message format templates
│
├── chad-yi/                     # A1 - You (master)
│   ├── MEMORY.md
│   ├── inbox/
│   ├── outbox/
│   └── delegated-tasks/
│
├── escritor/                    # A2 - Story Agent
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── SKILLS.md
│   ├── inbox/
│   ├── outbox/
│   ├── current-task.md
│   └── projects/                # A2 projects only
│       └── reunite/
│           ├── chapters/
│           ├── characters/
│           └── drafts/
│
├── autour/                      # A3 - Script Agent
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── SKILLS.md
│   ├── inbox/
│   ├── outbox/
│   ├── current-task.md
│   └── projects/
│       └── koe-scripts/
│           ├── drafts/
│           └── formatted/
│
├── quanta/                      # A5 - Trading Dev
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── SKILLS.md
│   ├── SECRETS.md               # API keys (encrypted)
│   ├── inbox/
│   ├── outbox/
│   ├── current-task.md
│   └── projects/
│       ├── trading-bots/
│       ├── strategies/
│       └── backtests/
│
└── [other agents...]
```

## Message Bus Protocol

### Message Format
```json
{
  "id": "MSG-20260209-001",
  "from": "escritor",
  "to": "quanta",
  "timestamp": "2026-02-09T13:00:00Z",
  "type": "request|response|update|alert",
  "subject": "Trading data for character",
  "body": "I need forex volatility data...",
  "priority": "high|normal|low",
  "attachments": [
    "path/to/file.md"
  ]
}
```

### Routing Rules
1. Agent writes to `outbox/message-XXX.md`
2. CHAD_YI (me) detects new message
3. I validate & route to recipient's `inbox/`
4. Recipient processes when active
5. Response written to sender's `inbox/`

## Activation Schedule

### Phase 1: Core (Today)
- ✅ CHAD_YI (already active)
- 🔄 Escritor (A2)
- 🔄 Autour (A3)

### Phase 2: Priority (Next)
- 🔄 Quanta (A5) - Trading Dev
- 🔄 MensaMusa - Trading Ops

### Phase 3: Operations
- 🔄 Helios (A6) - Mission Control
- 🔄 Atlas (C1) - Research

### Phase 4: Support
- 🔄 Remaining agents as needed

## Skill Specializations

Each agent gets:
- `SKILLS.md` - What they can do
- `tools/` - Tool configurations
- `templates/` - Reusable formats
- `knowledge/` - Reference materials

## Security Model

### Access Levels
- **Level 1 (Public)**: General project info
- **Level 2 (Agent)**: Agent-specific work
- **Level 3 (Private)**: API keys, credentials
- **Level 4 (Master)**: CHAD_YI only

### Isolation Rules
1. Agents cannot read other agents' SECRETS.md
2. Agents only see projects assigned to them
3. Cross-agent communication via message bus only
4. CHAD_YI audits all message routing

## Status: BUILDING