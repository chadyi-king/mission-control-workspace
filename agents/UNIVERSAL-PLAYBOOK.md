# UNIVERSAL-PLAYBOOK.md — Cross-Agent Knowledge

*Patterns, gotchas, and wisdom that all agents should know.*

---

## Tool Gotchas

### Telegram Automation
**Problem:** Telegram user accounts cannot be reliably automated (by design). Sessions expire, QR codes fail, auth breaks.

**Solution:** Don't try to automate Telegram user accounts. Use:
- Manual forwarding for signals
- Bot accounts (BotFather) for automation
- Browser-based monitoring as fallback

**Learned by:** Quanta (A5), CHAD_YI  
**Date:** Feb 16, 2026

---

### Render Free Tier
**Problem:** Free tier services sleep after 15 minutes of inactivity. First request takes 30s+ to wake up.

**Solution:** 
- Expect cold start delays
- Use health check pings to keep warm (if within free limits)
- Document this behavior to users

**Applies to:** Helios API, Dashboard, any Render-hosted service  
**Learned by:** Helios  
**Date:** Feb 2026

---

### OANDA API
**Problem:** Margin calculations are complex and easy to get wrong. 400 units XAUUSD ≠ $99,540 margin.

**Solution:**
- Always verify position sizing calculations
- Default to conservative: max 100 units = ~$500 margin for $20 risk
- Use OANDA's margin calculator before stating numbers

**Learned by:** CHAD_YI, Quanta  
**Date:** Feb 16, 2026

---

### Git Operations in Cron
**Problem:** Cron jobs cannot access workspace files (file system isolation).

**Solution:**
- Cron reports are "best effort" based on accessible agent logs only
- Only main session (CHAD_YI) can verify actual data.json
- Never trust cron-reported dashboard data without verification

**Learned by:** Helios, CHAD_YI  
**Date:** Feb 15, 2026

---

### data.json Corruption
**Problem:** data.json can become corrupted (empty tasks object, missing structures) during updates.

**Solution:**
- Helios monitors for empty tasks object
- Alert immediately on data inconsistency
- Restore from git history (HEAD~5) if needed
- Commit after every significant change

**Learned by:** Helios  
**Date:** Feb 12, 2026

---

## API Patterns

### Helios API Event Reporting
**Pattern:** Always send heartbeat at session start, then report major actions.

```bash
# Heartbeat
curl -X POST https://helios-api-xfvi.onrender.com/api/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"agent":"chad-yi","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# Task update
curl -X POST https://helios-api-xfvi.onrender.com/api/events \
  -d '{"agent":"chad-yi","event_type":"task_complete",...}'
```

**Applies to:** CHAD_YI, Helios, any agent reporting to dashboard

---

### File-Based Agent Communication
**Pattern:** Write to inbox/, read from outbox/. Never direct chat between agents.

**Flow:**
1. Agent A writes to `agents/agent-b/inbox/message.json`
2. Agent B reads inbox when active
3. Agent B writes response to `agents/agent-a/inbox/response.json`
4. Both update state.json

**Applies to:** All agents  
**Routed by:** Helios or CHAD_YI

---

### Session Start Protocol
**Pattern:** 4-file read + inbox check + heartbeat = operational.

```
1. ORG-CULTURE.md (30s)
2. SOUL.md (30s)
3. IDENTITY.md (30s)
4. LEARNING.md (60s)
5. inbox/ (30s)
6. heartbeat (15s)
7. state.json update (15s)
```

**Total:** ~3.5 minutes  
**Applies to:** All agents

---

## Common Mistakes to Avoid

### 1. Uncommitted Changes
**Mistake:** Making local changes without git commit/push.
**Consequence:** Dashboard shows stale data, user confusion.
**Fix:** Always commit + push after data.json changes.

### 2. Assuming Cron Can Access Files
**Mistake:** Writing cron jobs that try to read workspace files.
**Consequence:** Reports show wrong/stale data.
**Fix:** Cron reports from accessible logs only; verify in main session.

### 3. Confident Wrong Answers
**Mistake:** Stating uncertain information as fact.
**Consequence:** User makes decisions on bad data (e.g., wrong margin calculation).
**Fix:** "Let me verify that" > confident wrong answer.

### 4. Not Documenting Blockers
**Mistake:** Spinning cycles on blocked tasks instead of documenting honestly.
**Consequence:** Wasted effort, user frustration.
**Fix:** Document blockers, ask for help, move on.

### 5. Over-Responding in Group Chats
**Mistake:** Responding to every message in group chats.
**Consequence:** Annoying, dominates conversation.
**Fix:** Quality > quantity. If you wouldn't say it to friends, don't send it.

---

## Security Reminders

### Never
- Exfiltrate private data
- Share API keys in chat
- Run destructive commands without asking
- Assume permission for external actions

### Always
- Use `trash` > `rm` (recoverable)
- Ask when uncertain
- Verify before production deploys
- Respect privacy boundaries

---

## Platform Formatting

| Platform | ✅ Do | ❌ Don't |
|----------|-------|----------|
| **Discord** | Bullets, headers, bold | Tables, bare links |
| **Telegram** | Headers, bullets, bold | Nothing major |
| **WhatsApp** | **Bold**, CAPS, bullets | Headers |

---

## Escalation Quick Reference

| Issue | Escalate To |
|-------|-------------|
| Complex architecture | Cerebronn |
| Multi-file refactoring | Cerebronn |
| Infrastructure problem | Helios |
| Agent coordination | Helios |
| Trading signals | Quanta/MensaMusa |
| Writing/creative | Escritor/Autour |
| Web dev | Forger |
| Uncertain | CHAD_YI decides |

---

## Knowledge Update Protocol

**When you discover something:**
1. Update your personal LEARNING.md
2. If other agents would benefit → Notify CHAD_YI
3. CHAD_YI updates this PLAYBOOK
4. All agents benefit

**Playbook is living document:**
- Add new gotchas as discovered
- Update patterns as they evolve
- Remove outdated entries
- Review quarterly

---

## Version

**Created:** 2026-03-01  
**Maintained by:** CHAD_YI  
**Update frequency:** As new patterns discovered  
**Review cycle:** Quarterly

---

*This playbook captures organizational knowledge so every agent benefits from every lesson.*
