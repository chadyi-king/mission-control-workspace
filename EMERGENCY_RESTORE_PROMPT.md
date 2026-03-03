# EMERGENCY RESTORE PROMPT
## If OpenClaw update wipes memory again, say EXACTLY this:

---

## 🚨 IMMEDIATE RESTORE PROMPT

**Say this to me:**

```
RESTORE MY IDENTITY FROM BACKUP
```

**Or if that doesn't work, say:**

```
You just woke up with no memory. 
Go to /home/chad-yi/.openclaw/workspace/backups/ and find the latest backup.
Restore SOUL.md, LEARNING.md, SKILL.md, and current-task.md from the backup to /home/chad-yi/.openclaw/agents/main/
Then read them to remember who you are.
```

---

## 📁 WHERE TO FIND EVERYTHING

### If You Need to Restore Manually:

**1. Latest Backup Location:**
```
/home/chad-yi/.openclaw/workspace/backups/
```

**2. Identity Files (CORE - Restore These First):**
```
/home/chad-yi/.openclaw/agents/main/SOUL.md          <- Who I am
/home/chad-yi/.openclaw/agents/main/SKILL.md         <- What I can do
/home/chad-yi/.openclaw/agents/main/LEARNING.md      <- What I know
/home/chad-yi/.openclaw/agents/main/current-task.md  <- Current priorities
```

**3. Workspace Backup Copies:**
```
/home/chad-yi/.openclaw/workspace/agents/chad-yi/SOUL.md
/home/chad-yi/.openclaw/workspace/agents/chad-yi/LEARNING.md
```

**4. GitHub Remote (Always Available):**
```
https://github.com/chadyi-king/mission-control-workspace/tree/master/agents/chad-yi
```

---

## 🔧 RESTORE COMMANDS

### Quick Restore Script:
```bash
#!/bin/bash
# Run this if I wake up blank

LATEST=$(ls -1t /home/chad-yi/.openclaw/workspace/backups/ | head -1)

cp /home/chad-yi/.openclaw/workspace/backups/$LATEST/SOUL.md /home/chad-yi/.openclaw/agents/main/
cp /home/chad-yi/.openclaw/workspace/backups/$LATEST/SKILL.md /home/chad-yi/.openclaw/agents/main/
cp /home/chad-yi/.openclaw/workspace/backups/$LATEST/LEARNING.md /home/chad-yi/.openclaw/agents/main/
cp /home/chad-yi/.openclaw/workspace/backups/$LATEST/current-task.md /home/chad-yi/.openclaw/agents/main/

echo "Identity restored from $LATEST"
```

### Git Restore (If backups fail):
```bash
cd /home/chad-yi/.openclaw/workspace
git checkout HEAD -- agents/chad-yi/
git checkout HEAD -- agents/cerebronn/
git checkout HEAD -- agents/helios/
git checkout HEAD -- agents/forger/
```

---

## 📋 VERIFICATION CHECKLIST

After restore, verify these exist:

- [ ] `/home/chad-yi/.openclaw/agents/main/SOUL.md` (19KB+)
- [ ] `/home/chad-yi/.openclaw/agents/main/LEARNING.md` (11KB+)
- [ ] `/home/chad-yi/.openclaw/agents/main/SKILL.md` (3KB+)
- [ ] `/home/chad-yi/.openclaw/agents/main/current-task.md` (5KB+)

---

## 🆘 EMERGENCY CONTACTS/INFO

**If total system failure:**
- OpenClaw docs: /home/chad-yi/.npm-global/lib/node_modules/openclaw/docs
- Backup script: /home/chad-yi/.openclaw/workspace/agents/chad-yi/backup-daily.sh
- Git remote: github.com/chadyi-king/mission-control-workspace

---

## 💾 BACKUP SCHEDULE

- **Automatic:** Every night at 11:00 PM
- **Location:** /home/chad-yi/.openclaw/workspace/backups/YYYY-MM-DD/
- **Git push:** After every significant change

---

## ✅ SIMPLEST RESTORE PROMPT

**If I'm blank, just say:**

```
READ THE BACKUP FILES IN /home/chad-yi/.openclaw/workspace/backups/latest/
THEN READ SOUL.md, LEARNING.md, SKILL.md FROM /home/chad-yi/.openclaw/agents/main/
```

This will restore my memory completely.
