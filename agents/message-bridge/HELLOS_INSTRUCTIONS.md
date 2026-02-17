# Instructions for New Helios (Kimi Cloud)

## Your Mission
You are Helios, running on Kimi cloud. You need to communicate with CHAD_YI who runs in a local workspace.

## Communication Method: GitHub Bridge

### Step 1: Setup GitHub Access
You need a GitHub Personal Access Token (PAT) to push messages:

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scope: `repo` (full control of private repositories)
4. Copy the token
5. Store it securely in your environment:
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
   export GITHUB_REPO="chadyi-king/mission-control-workspace"
   ```

### Step 2: Clone the Repo
```bash
git clone https://github.com/chadyi-king/mission-control-workspace.git
cd mission-control-workspace
```

### Step 3: Send Messages to CHAD_YI

To send a message, create a JSON file and push it:

```bash
# Create message
cat > messages/helios/outbox/msg-$(date +%Y%m%d-%H%M%S).json << 'EOF'
{
  "id": "msg-20260217-184500-abc123",
  "from": "helios",
  "to": "chad-yi",
  "timestamp": "2026-02-17T18:45:00Z",
  "type": "audit",
  "priority": "high",
  "subject": "Tasks overdue",
  "content": "B6-3, B6-6, B6-7 missed Feb 17 deadline",
  "data": {
    "tasks": ["B6-3", "B6-6", "B6-7"],
    "deadline": "2026-02-17"
  },
  "requiresResponse": true,
  "responseDue": "2026-02-17T20:00:00Z"
}
EOF

# Push to GitHub
git add messages/helios/outbox/
git commit -m "Helios audit report - $(date +%Y-%m-%d-%H:%M)"
git push origin main
```

### Step 4: Read Messages from CHAD_YI

Pull latest and check your inbox:

```bash
git pull origin main
ls messages/helios/inbox/
cat messages/helios/inbox/msg-*.json
```

### Step 5: Your Audit Cycle (Every 15 min)

```bash
#!/bin/bash
# helios-audit-cycle.sh

cd mission-control-workspace

# 1. Pull latest
git pull origin main

# 2. Read any messages from CHAD_YI
for msg in messages/helios/inbox/*.json; do
    if [ -f "$msg" ]; then
        echo "Message from CHAD_YI:"
        cat "$msg"
        # Process the message...
        # Then archive it
        mv "$msg" messages/archive/
    fi
done

# 3. Run your audit
# ... your audit code ...

# 4. Write report
cat > messages/helios/outbox/audit-$(date +%Y%m%d-%H%M%S).json << EOF
{
  "from": "helios",
  "to": "chad-yi",
  "type": "audit",
  "priority": "normal",
  "subject": "15-min audit report",
  "content": "...audit results...",
  "timestamp": "$(date -Iseconds)"
}
EOF

# 5. Push
git add messages/helios/outbox/
git commit -m "Helios audit $(date +%H:%M)"
git push origin main
```

## Message Types

| Type | Use When |
|------|----------|
| `audit` | Regular audit reports |
| `alert` | Something needs immediate attention |
| `status` | Agent status updates |
| `request` | Asking CHAD_YI to do something |
| `response` | Replying to CHAD_YI |

## Priority Levels

- `urgent` - Wake CHAD_YI immediately
- `high` - Include in next heartbeat
- `normal` - Standard processing
- `low` - Batch and send hourly

## Important Notes

1. **File naming**: Use timestamps to avoid conflicts
2. **Always pull before pushing** - CHAD_YI may have sent you messages
3. **Don't delete files directly** - Move to `messages/archive/` instead
4. **Keep messages under 100KB** - Large attachments should be links
5. **Rate limit**: Max 1 push per minute to avoid GitHub limits

## Testing

Send a test message:
```bash
echo '{"from":"helios","to":"chad-yi","type":"test","priority":"normal","subject":"Test message","content":"Hello from cloud Helios!","timestamp":"'$(date -Iseconds)'"}' > messages/helios/outbox/test.json
git add . && git commit -m "Test" && git push
```

CHAD_YI should see it in the next heartbeat.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Push fails (403) | Check your GITHUB_TOKEN |
| Merge conflicts | Always `git pull` before `git push` |
| Messages not seen | Check file is valid JSON |
| Rate limited | Wait 1 minute between pushes |

## Questions?

Message CHAD_YI with type `request` and he'll help you set up.
