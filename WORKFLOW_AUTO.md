# WORKFLOW_AUTO.md - Automated Agent Workflow

## Overview
This document defines the automated workflow for file-based agent coordination.

## Communication Pattern

```
Human/CHAD_YI → Agent inbox/ → Agent processes → Agent outbox/ → Human/CHAD_YI reads
```

## Directory Structure

Each agent has:
```
agents/<agent-name>/
├── inbox/      # Tasks to process (JSON files)
├── outbox/     # Results (JSON files)
├── logs/       # Agent logs
└── *.py        # Agent code
```

## Task Format (inbox/)

```json
{
  "id": "unique-task-id",
  "type": "TASK_TYPE",
  "param1": "value",
  "param2": "value"
}
```

## Result Format (outbox/)

```json
{
  "task_id": "unique-task-id",
  "timestamp": "2026-03-06T06:42:00+00:00",
  "success": true,
  "data": { ... },
  "error": "error message if failed"
}
```

## Agent Status

| Agent | Status | Purpose |
|-------|--------|---------|
| gws-agent | Ready | Google Workspace integration |
| helios | Running | Mission Control coordination |
| chad-yi | Running | Main interface |

## Service Management

```bash
# Start agent
systemctl --user start <agent-name>

# Stop agent
systemctl --user stop <agent-name>

# Enable auto-start
systemctl --user enable <agent-name>
```

## Adding New Tasks

1. Create JSON file in agent's `inbox/`
2. Agent detects file (polls every 30s)
3. Agent processes task
4. Agent writes result to `outbox/`
5. Agent deletes processed task from `inbox/`

## Error Handling

- Failed tasks still produce output in outbox/
- Check `error` field in result
- Logs in `logs/<agent-name>.log`
