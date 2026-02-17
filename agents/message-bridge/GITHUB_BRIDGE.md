# Helios-CHAD_YI GitHub Bridge

## Purpose
Enable the new Helios (running on Kimi cloud) to communicate with CHAD_YI (local workspace) via GitHub.

## How It Works

### Message Flow: Helios → CHAD_YI
1. Helios writes message to `messages/helios/outbox/[timestamp].json`
2. Helios commits and pushes to GitHub
3. CHAD_YI pulls the repo
4. CHAD_YI reads messages and routes to local message bus
5. CHAD_YI archives processed messages

### Message Flow: CHAD_YI → Helios
1. CHAD_YI writes response to `messages/chad-yi/outbox/[timestamp].json`
2. CHAD_YI commits and pushes to GitHub
3. Helios pulls and reads responses

## Directory Structure (GitHub Repo)
```
mission-control-workspace/
├── messages/
│   ├── helios/
│   │   ├── outbox/      # Helios writes here
│   │   └── inbox/       # Helios reads responses here
│   ├── chad-yi/
│   │   ├── outbox/      # CHAD_YI writes here
│   │   └── inbox/       # CHAD_YI reads messages here
│   └── archive/         # Processed messages
├── AGENT_STATE.json     # Shared agent state
└── dashboard-sync.json  # Dashboard data sync
```

## Message Format
```json
{
  "id": "msg-20260217-154200-abc123",
  "from": "helios",
  "to": "chad-yi",
  "timestamp": "2026-02-17T15:42:00Z",
  "type": "audit|status|alert|request|response",
  "priority": "low|medium|high|urgent",
  "subject": "Brief description",
  "content": "Full message body",
  "data": {},
  "requiresResponse": true,
  "responseDue": "2026-02-17T16:00:00Z"
}
```

## Authentication
- Helios uses GitHub Personal Access Token (PAT)
- Token needs `repo` scope
- Stored in Helios environment variables (not in code)

## Sync Frequency
- Helios: Push every 15 minutes (after audit)
- CHAD_YI: Pull every heartbeat (30 min)
- Both: Pull before sending

## Conflict Resolution
- Use timestamps in filenames
- Last-write-wins for AGENT_STATE.json
- Messages are append-only (no conflicts)

## Status
- [ ] GitHub PAT configured
- [ ] Helios pushing messages
- [ ] CHAD_YI pulling messages
- [ ] Auto-sync working
