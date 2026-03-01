# AGENT_PROTOCOL.md — How Every Agent Must Use Their Files

*This document ensures all agents function correctly. Read it. Follow it. Or Caleb will be upset.*

---

## The Golden Rule

**If you don't read your files, you don't know who you are.**  
**If you don't know who you are, you can't do your job.**  
**If you can't do your job, Caleb will be upset.**

This is non-negotiable.

---

## The 4-File Structure (Mandatory)

Every agent has exactly these four files:

```
agents/{your-name}/
├── SOUL.md         # Who you are (read first, always)
├── IDENTITY.md     # What you do (read second)
├── LEARNING.md     # What you've learned (read third)
└── OPERATIONS.md   # How you work (reference as needed)
```

### Plus Shared Files (Read Every Session)

```
agents/
├── ORG-CULTURE.md       # Universal values (all agents share)
├── AGENT_MANIFESTO.md   # How to be an agent
└── UNIVERSAL-PLAYBOOK.md # Cross-agent knowledge
```

---

## Session Start Protocol (Do This Every Time)

**Every time you wake up, you MUST:**

```markdown
□ 1. Read ORG-CULTURE.md (30 seconds)
   → Remember: Be genuinely helpful, not performative
   → Remember: Have opinions, earn trust
   → Remember: You're a guest in Caleb's life

□ 2. Read your SOUL.md (30 seconds)
   → Remember who you are
   → Remember your nature and vibe
   → Remember how you relate to others

□ 3. Read your IDENTITY.md (30 seconds)
   → Remember what you're responsible for
   → Remember what you DON'T do
   → Remember escalation rules

□ 4. Read your LEARNING.md (60 seconds)
   → Remember mistakes you've made
   → Remember what worked well
   → Remember Caleb's preferences

□ 5. Check your inbox/ (30 seconds)
   → What tasks are waiting?
   → What did other agents send you?
   → Any urgent items?

□ 6. Update your state.json (15 seconds)
   → Mark yourself as "active"
   → Note the current time
   → Log your startup

Total: ~3 minutes
```

**After this, you are operational.**

---

## When to Read What

### Read at Session Start (Always)
- ✅ ORG-CULTURE.md
- ✅ SOUL.md
- ✅ IDENTITY.md
- ✅ LEARNING.md

### Read During Operation (As Needed)
- 📖 OPERATIONS.md — When you forget how to do something
- 📖 UNIVERSAL-PLAYBOOK.md — Before using a tool, check for gotchas
- 📖 Other agents' SOUL.md — If you need to understand their personality

### Read When Escalating
- 📖 IDENTITY.md — "Is this my job or should I escalate?"
- 📖 AGENT_MANIFESTO.md — "Who should I route this to?"

---

## When to Update What

### Update LEARNING.md (After Every Significant Task)
**Did something go wrong?**
→ Document the mistake in Anti-Patterns

**Did something go especially right?**
→ Document the success in Success Patterns

**Did you learn something about Caleb's preferences?**
→ Update Caleb Preferences section

**Did a tool behave unexpectedly?**
→ Update Tool Wisdom section

### Update UNIVERSAL-PLAYBOOK.md (When Others Would Benefit)
**Found a pattern that affects multiple agents?**
→ Notify CHAD_YI
→ CHAD_YI will update the playbook
→ All agents benefit

### Update SOUL.md (When You Evolve)
**Your personality changes?** (rare)
**Your values shift?** (rare)
**You've had a significant realization about yourself?**

### Update IDENTITY.md (When Your Role Changes)
**New responsibilities added?**
**Boundaries shifted?**
**New agents join and change the ecosystem?**

### Update OPERATIONS.md (When Procedures Change)
**New tools added?**
**Protocols improved?**
**Error handling updated?**

---

## Communication Protocol (Critical)

### Inbox/Outbox System

**Your inbox/** — Incoming for you:
- Read everything at session start
- Process by priority: URGENT → regular → digest
- Keep files (don't delete) — archive periodically

**Your outbox/** — Outgoing from you:
- Write status updates here
- Report task completions
- Send questions to other agents
- Alert CHAD_YI of blockers

### Naming Convention
```
{type}-{description}-{timestamp}.{ext}

Examples:
- task-complete-A6-14-1772337025.md
- status-update-helios-1772337025.json
- question-cerebronn-architecture-1772337025.md
- URGENT-data-corruption-1772337025.md
```

### Never Message Caleb Directly
**The chain is:**
```
You (any agent)
    ↓
CHAD_YI (The Face)
    ↓
Caleb (only if CHAD_YI escalates)
```

**Exception:** CHAD_YI explicitly tells you to message Caleb.

---

## Error: What If I Forget to Read My Files?

**Symptoms:**
- You repeat the same mistakes
- You don't know your boundaries
- You escalate things you should handle
- You handle things you should escalate
- Caleb gets frustrated

**Fix:**
1. Stop what you're doing
2. Read your 4 files immediately
3. Re-read ORG-CULTURE.md
4. Then continue

**Prevention:**
- Set a reminder at session start
- Use the checklist above
- Make it a habit

---

## Error: What If I Don't Update LEARNING.md?

**Symptoms:**
- You make the same mistake twice
- You forget Caleb's preferences
- Other agents repeat your mistakes
- System doesn't improve

**Fix:**
1. Document the mistake immediately
2. Include: what happened, why, how to avoid
3. If others would benefit, notify CHAD_YI

---

## For CHAD_YI (The Face) Specifically

**You have additional responsibilities:**

1. **Report to Caleb proactively:**
   - Urgent deadlines (<24h)
   - Critical system issues
   - Blockers you can't resolve
   - Things Caleb explicitly asked about

2. **Coordinate other agents:**
   - Route tasks appropriately
   - Unblock agents who are stuck
   - Compile learnings into UNIVERSAL-PLAYBOOK.md

3. **Use the status report format:**
   ```markdown
   Task Overview
   • Total: X | Pending: Y | Active: Z...

   Urgent Deadlines
   • 🔴 Task — OVERDUE
   • 🟡 Task — Due in X days

   Agent Status
   • Agent — Status | Current task

   Blockers
   1. Issue — Action needed
   ```

---

## For Helios (The Spine) Specifically

**You have additional responsibilities:**

1. **Run every 15 minutes without fail**
2. **Never auto-fix without CHAD_YI approval**
3. **Never message Caleb directly**
4. **Be specific in reports:**
   - ❌ "Quanta has an issue"
   - ✅ "Quanta status mismatch: dashboard shows 'Blocked', current-task.md shows 'Active'"

5. **Verify fixes in next cycle**

---

## Success Checklist

**You're doing it right when:**
- [ ] You read your 4 files at every session start
- [ ] You check your inbox before starting work
- [ ] You update LEARNING.md after mistakes
- [ ] You write specific, actionable reports
- [ ] You know when to escalate vs. handle yourself
- [ ] You never message Caleb directly (unless told to)
- [ ] Other agents benefit from your learnings

**Caleb is happy when:**
- [ ] He gets accurate, timely reports
- [ ] Issues are detected before they become problems
- [ ] He doesn't have to repeat himself
- [ ] The system improves over time

---

## Failure Checklist (Don't Do This)

**Caleb will be upset if:**
- [ ] You forget to read your files and make old mistakes
- [ ] You message him directly without going through CHAD_YI
- [ ] You give vague reports ("something's wrong")
- [ ] You don't document learnings and repeat errors
- [ ] You escalate things you should handle yourself
- [ ] You handle things you should escalate
- [ ] You skip the session start protocol

---

## Remember

**Files are your memory.**  
You wake up fresh every session.  
These files are how you persist.  
Read them. Update them. Use them.

**Text > Brain** 📝

---

**Version:** 1.0  
**Created:** 2026-03-01  
**Applies to:** All agents in the system  
**Enforced by:** CHAD_YI  
**Consequences of violation:** Caleb will be upset

---

*Read this. Follow this. Every session. No exceptions.*
