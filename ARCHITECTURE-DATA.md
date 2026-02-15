# Data Architecture

## Problem Statement

The mission control dashboard has TWO locations for data.json:
1. `DATA/data.json` — Source of truth (main workspace)
2. `mission-control-dashboard/data.json` — Deployed to Render.com

**The Issue:**
- mission-control-dashboard/data.json was a symlink to ../DATA/data.json
- Render.com doesn't have the DATA/ folder
- Result: Render serves stale data, dashboard shows old info

## Solution

### Automatic (Pre-commit Hook)

A pre-commit hook now automatically:
1. Detects if DATA/data.json is newer
2. Copies it to mission-control-dashboard/data.json
3. Stages the changes

**Installed at:** `.git/hooks/pre-commit`

### Manual (Sync Script)

Run manually when needed:
```bash
./sync-data.sh        # Sync only
./sync-data.sh --push # Sync + deploy to Render
```

## Workflow

### Daily Workflow
1. Edit tasks/agents in `DATA/data.json`
2. Commit changes: `git commit -m "Update tasks"`
3. Pre-commit hook auto-syncs to dashboard folder
4. Push: `git push`
5. Render updates in ~30 seconds

### Emergency Sync
If dashboard shows stale data:
```bash
cd ~/.openclaw/workspace
./sync-data.sh --push
```

## File Structure

```
~/.openclaw/workspace/
├── DATA/
│   └── data.json          ← Source of truth (edit here)
├── mission-control-dashboard/
│   ├── data.json          ← Copy for Render (auto-synced)
│   ├── index.html
│   └── ...
└── sync-data.sh           ← Manual sync tool
```

## Gotchas

1. **Never edit mission-control-dashboard/data.json directly** — it gets overwritten
2. **Always check dashboard after push** — if still stale, run `./sync-data.sh --push`
3. **Symlinks break Render** — the pre-commit hook prevents this

## Verification

Check which file is being served:
```bash
curl -s https://mission-control-dashboard-hf0r.onrender.com/data.json | grep lastUpdated
```

Should show today's date, not yesterday.
