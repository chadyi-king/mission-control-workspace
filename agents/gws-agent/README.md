# Google Workspace Agent (gws-agent)

## Quick Start

```bash
# 1. Start the agent
systemctl --user start gws-agent

# 2. Test with a task
cp SAMPLE_TASK.json inbox/

# 3. Check result
cat outbox/test-001.json

# 4. View logs
tail -f logs/gws-agent.log
```

## Task Format

Drop JSON files in `inbox/`:

```json
{
  "id": "unique-id",
  "type": "TASK_TYPE",
  "param1": "value"
}
```

## Supported Tasks

| Task Type | Params | Description |
|-----------|--------|-------------|
| `GMAIL_LIST` | `limit`, `label` | List emails |
| `GMAIL_SEND` | `to`, `subject`, `body` | Send email |
| `DRIVE_LIST` | `folder` | List Drive files |
| `DRIVE_UPLOAD` | `local_path`, `folder` | Upload file |
| `SHEETS_READ` | `sheet_id`, `range` | Read spreadsheet |
| `SHEETS_APPEND` | `sheet_id`, `values` | Append row |
| `CALENDAR_LIST` | none | List events |

## Examples

**Send Email:**
```json
{
  "id": "email-001",
  "type": "GMAIL_SEND",
  "to": "person@example.com",
  "subject": "Hello",
  "body": "Message here"
}
```

**List Drive:**
```json
{
  "id": "drive-001",
  "type": "DRIVE_LIST"
}
```

**Append to Sheet:**
```json
{
  "id": "sheet-001",
  "type": "SHEETS_APPEND",
  "sheet_id": "YOUR_SHEET_ID",
  "values": ["2026-03-06", "Task", "Done"]
}
```

## Service Commands

```bash
# Start
systemctl --user start gws-agent

# Stop
systemctl --user stop gws-agent

# Status
systemctl --user status gws-agent

# Logs
journalctl --user -u gws-agent -f
```
