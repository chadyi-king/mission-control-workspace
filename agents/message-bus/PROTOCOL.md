# Agent Message Bus Protocol

## How Agents Communicate

### File-Based Messaging
All agents communicate through files in `/agents/message-bus/`:
- **broadcast/** - Messages for all agents
- **direct/[agent-id]/** - Messages for specific agent
- **archive/** - Completed/resolved messages

### Message Format
```json
{
  "id": "msg-[timestamp]-[uuid]",
  "from": "agent-id",
  "to": "agent-id|broadcast",
  "timestamp": "2026-02-11T08:35:00Z",
  "type": "status|request|response|alert|audit",
  "priority": "low|medium|high|urgent",
  "subject": "Brief description",
  "content": "Full message",
  "requiresAction": true|false,
  "actionBy": "agent-id|null"
}
```

## Helios ↔ CHAD_YI Coordination

### Helios (Every 15 min):
1. Runs audit checks
2. Auto-fixes small issues
3. Writes report to outbox
4. If urgent: writes to message-bus/broadcast/
5. Updates AGENT_STATE.json

### CHAD_YI (Hourly):
1. Checks message-bus/broadcast/ for urgent items
2. Reads Helios audit reports
3. Takes action on issues
4. Notifies user if needed
5. Archives processed messages

## Current Agents
| Agent | Status | Current Task | Last Update |
|-------|--------|--------------|-------------|
| CHAD_YI | Active | Orchestrating | Real-time |
| Helios | Active | 15-min audits | Next: 08:45 |
| Escritor | Idle | Waiting for work | 2026-02-09 |

## Active Jobs
- Morning Briefing: 8 AM daily
- 2-hour Check-in: 10/12/14/16/18/20/22
- Night Check: 0/3/6 AM
- Helios Audit: Every 15 minutes
- Hourly Coordination: :30 every hour