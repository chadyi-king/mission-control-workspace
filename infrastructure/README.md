# Agent Infrastructure Architecture

## Components

### 1. WebSocket Message Hub (Port 9000)
- Real-time communication between all agents
- Pub/sub pattern: agents subscribe to channels
- Channels: broadcast, agent-specific, task-specific

### 2. Tool Bridge Service
- Provides agents with actual tool capabilities
- REST API: /exec, /browser, /image-gen, /file-write
- Each agent authenticates with token

### 3. Agent Supervisor
- Monitors all agent processes
- Auto-restarts crashed agents
- Health checks every 30 seconds
- Reports to CHAD_YI on failures

### 4. Shared Memory Service
- Centralized memory store
- All agents read/write to same memory
- No more "I forgot" - persistent across sessions

### 5. Tailscale Mesh (Future)
- Secure networking between agents
- Can be added later without breaking existing setup

## File Structure
```
infrastructure/
├── hub/
│   ├── websocket-server.py
│   └── config.json
├── tool-bridge/
│   ├── server.py
│   └── api-keys.json (gitignored)
├── supervisor/
│   ├── monitor.py
│   └── agents.conf
├── shared-memory/
│   ├── memory-server.py
│   └── store/
└── install.sh
```
