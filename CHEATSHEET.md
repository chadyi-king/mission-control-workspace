# CHAD_YI CHEAT SHEET
## Quick Reference (Keep This Handy)

**If I forget everything, read this file.**

---

## EMERGENCY RECOVERY

**If data corrupted:**
```bash
cd /home/chad-yi/.openclaw/workspace
./scripts/restore.sh data-20260212-235320-TEST-BEFORE-MIGRATION.json
python3 scripts/verify-data.py
```

**If you forget the backup filename:**
```bash
./scripts/list-backups.sh
```

---

## THE 3 GOLDEN RULES

1. **DATA IS SACRED** - Only I write to DATA/data.json
2. **BACKUP BEFORE CHANGE** - Always run backup script first  
3. **DASHBOARD IS READ-ONLY** - Symlink, cannot corrupt data

---

## AGENT CREATION (10 Steps)

```bash
# 1. Copy template
cp -r agents/_templates/new-agent/ agents/[NAME]/

# 2. Fill contract.yaml (name, role, skills)

# 3. Create MEMORY.md (knowledge)

# 4. Setup folders
mkdir -p agents/[NAME]/inbox agents/[NAME]/outbox

# 5. Copy state.json
cp agents/_templates/new-agent/state.json agents/[NAME]/

# 6. Create .env for secrets
touch agents/[NAME]/.env

# 7. Backup data first
./scripts/backup-before-change.sh "PRE-AGENT-[NAME]"

# 8. Register in DATA/data.json (agents section)

# 9. Verify
python3 scripts/verify-data.py

# 10. Commit
git add -A
git commit -m "Created agent [NAME]"
git push
```

---

## DAILY WORKFLOW

**When I start working:**
1. Read SOUL.md
2. Read agents/chad-yi/MEMORY.md  
3. Read memory/2026-02-13.md
4. Check DATA/data.json status
5. Report to Caleb: "Here's where we are..."

**Before any data change:**
1. ./scripts/backup-before-change.sh "REASON"
2. Make change
3. python3 scripts/verify-data.py
4. git add -A && git commit -m "..." && git push

---

## KEY LOCATIONS

| What | Where |
|------|-------|
| All tasks | DATA/data.json |
| My memory | agents/chad-yi/MEMORY.md |
| Today's log | memory/2026-02-13.md |
| Backups | DATA/backups/manual/ |
| Agent template | agents/_templates/new-agent/ |
| Dashboard | mission-control-dashboard/ |
| Scripts | scripts/ |

---

## VERIFICATION CHECKLIST

Before claiming something works:
- [ ] Tested backup/restore?
- [ ] Verified data integrity?
- [ ] Checked git status?
- [ ] Documented in memory?

---

## IF CALEB ASKS

**"Is it safe?"**
→ YES. Data separated, backed up, read-only dashboard.

**"How do I add a task?"**
→ Tell me on Telegram. I backup → write to DATA/ → push → dashboard updates.

**"What if you fuck up?"**
→ 1 command restore from backup. Git history. Never lose data again.

**"How do I create an agent?"**
→ 10-step checklist above. I handle all technical parts.

---

*This is my memory. Read it if I forget.*
