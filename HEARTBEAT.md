# HEARTBEAT.md — Infra Stabilization Mode

## Purpose
Use heartbeats to keep the infrastructure honest until the system is stable.

## Every heartbeat, do this
1. Run:
```bash
bash /home/chad-yi/.openclaw/workspace/scripts/infra_audit_snapshot.sh
```
2. If output contains only `OK:` / `INFO:` and ends with `SUMMARY: HEALTHY` → reply exactly:
`HEARTBEAT_OK`
3. If output contains any `ISSUE:` lines:
- report only the broken items
- keep it short
- include the exact failing component
- if Quanta is involved, mention `dry_run` and `open_trades`
4. If active infrastructure cleanup is in progress, use the heartbeat as a hard self-check:
- continue the cleanup work
- do not drift to side quests
- if more than ~45 minutes have passed since the last meaningful Caleb update and there is real progress or a blocker, send a concise checkpoint
- do not send filler just to satisfy the timer

## What matters most
- `openclaw-gateway` up
- `helios` up
- `cerebronn` up
- `forger` up
- old junk services OFF:
  - `mc-websocket`
  - `gws-agent`
  - old `quanta.service`
  - `chad-report-delivery`
- Quanta v3 process alive + heartbeat fresh
- live dashboard reachable:
  - `https://red-sun-mission-control.onrender.com`
- dashboard repo not dirty
- `ACTIVE.md` not stale

## Reporting style
Bad:
- long essay
- healthy noise
- vague "something is wrong"

Good:
```text
Infra alert
• quanta-v3 process not running
• mission-control-dashboard repo dirty
• ACTIVE.md stale
```

If nothing is wrong, say only:
`HEARTBEAT_OK`
