# Agent Check-In Protocol

## Problem
Helios can see FILE timestamps but not PROGRESS. An agent could:
- Have old file (looks idle to Helios)
- But actually be working for hours without saving
- Or be stuck/blocked but file looks "active"

## Solution: Agent Heartbeat
Every agent must write a heartbeat file every 30 minutes when working.

### Location
`/agents/[agent-name]/heartbeat.json`

### Format
```json
{
  "agent": "escritor",
  "timestamp": "2026-02-11T08:45:00Z",
  "status": "working|idle|blocked|waiting",
  "currentTask": "Edit Chapter 13",
  "progress": "50%",
  "eta": "2 hours",
  "blockers": null,
  "lastOutput": "Analyzed first half of chapter"
}
```

### Helios Monitors
- If heartbeat >1 hour old → agent is stale
- If status="blocked" → Alert CHAD_YI immediately
- If progress not changing → agent might be stuck

## Implementation

### For Escritor (A2 - Story Agent)
When working on Chapter 13:
1. Read chapter content
2. Analyze and write notes
3. **Every 30 min:** Update heartbeat.json
4. When done: Write to outbox/, mark complete in heartbeat

### For Quanta (A5 - Trading Dev)
When blocked:
1. Update heartbeat.json: status="blocked", blockers="Need OANDA account"
2. Helios sees immediately
3. Alert escalates to CHAD_YI
4. CHAD_YI notifies user

### For Autour (A3 - Script Agent)
When idle:
1. heartbeat.json: status="idle", currentTask=null
2. Helios knows no work assigned
3. CHAD_YI can assign new scripts

## Helios Integration

### 15-Min Audit Now Checks:
1. ✅ File timestamps (existing)
2. ✅ **NEW:** Heartbeat freshness
3. ✅ **NEW:** Progress tracking
4. ✅ **NEW:** Blocker detection

### Auto-Fixes:
- Stale heartbeat (>1h) → Mark agent "unresponsive"
- Blocked status → Immediate alert (not hourly)
- No progress 2+ hours → Flag as "potentially stuck"

## Files Created
- `/agents/escritor/heartbeat.json` - Escritor's current status
- `/agents/quanta/heartbeat.json` - Quanta's current status
- `/agents/autour/heartbeat.json` - Autour's current status